"""Path, identifier, and resource-limit helpers for datapack generation.

Minecraft datapack identifiers (namespace, function path segments, etc.)
follow a restricted character set. User-controlled values that end up in
filesystem or ZIP paths must be validated before use.

guigenmc does not execute OS shell commands from config. Minecraft command
strings in the config are embedded into the generated datapack as-is; that
is intentional and is not an OS command-injection surface.
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

# Minecraft resource location path segment (namespace / path parts):
# lowercase a-z, 0-9, underscore, hyphen, period. No slashes or spaces.
# See: https://minecraft.wiki/w/Resource_location
_IDENTIFIER_RE = re.compile(r"^[a-z0-9._-]+$")

# ---------------------------------------------------------------------------
# Resource limits (DoS / archive-bomb style protections)
# ---------------------------------------------------------------------------

# Max nesting depth of the parsed JSON config object.
MAX_JSON_DEPTH = 64

# Max number of JSON values (objects, arrays, scalars) walked while checking.
MAX_JSON_NODES = 100_000

# Max files a single generate_datapack() call may produce.
MAX_GENERATED_FILES = 5_000

# Max total UTF-8 byte size of all generated file contents combined.
MAX_GENERATED_TOTAL_BYTES = 50 * 1024 * 1024  # 50 MiB


def validate_identifier(value: str, field_name: str = "identifier") -> str:
    """Validate a Minecraft-style identifier used in datapack paths.

    Raises ValueError with a clear message if the value is unsafe.
    Returns the validated string unchanged on success.
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid {field_name}: must be a string")
    if not value:
        raise ValueError(f"Invalid {field_name}: must not be empty")
    if "\x00" in value:
        raise ValueError(f"Invalid {field_name}: contains NULL byte")
    if "/" in value or "\\" in value:
        raise ValueError(f"Invalid {field_name}: contains path separator")
    if ".." in value:
        raise ValueError(f"Invalid {field_name}: contains parent-directory segment")
    if value.startswith(".") or value.endswith("."):
        # Leading/trailing dots are unusual and can confuse path logic.
        raise ValueError(f"Invalid {field_name}: must not start or end with '.'")
    if not _IDENTIFIER_RE.match(value):
        raise ValueError(
            f"Invalid {field_name}: {value!r} — only lowercase a-z, 0-9, "
            f"underscore, hyphen and period are allowed (Minecraft resource location rules)"
        )
    return value


def is_safe_relative_path(rel: str) -> bool:
    """Return True if *rel* is a safe relative path for filesystem/ZIP use.

    Rejects absolute paths, parent traversal, backslashes, NULL bytes,
    Windows drive letters, and empty segments that would escape a root.
    """
    if not isinstance(rel, str) or not rel:
        return False
    if "\x00" in rel:
        return False
    # Reject Windows-style separators and drive paths early.
    if "\\" in rel:
        return False
    if len(rel) >= 2 and rel[1] == ":" and rel[0].isalpha():
        return False
    # Reject absolute Unix paths.
    if rel.startswith("/"):
        return False
    # Normalize with PurePosixPath so platform does not matter.
    try:
        p = PurePosixPath(rel)
    except Exception:
        return False
    if p.is_absolute():
        return False
    parts = p.parts
    if not parts:
        return False
    for part in parts:
        if part in ("", ".", ".."):
            return False
        if "\x00" in part:
            return False
    return True


def ensure_within_output_root(out_dir: Path, rel: str) -> Path:
    """Resolve *rel* under *out_dir* and ensure it stays inside the root.

    Raises ValueError if the resolved path would escape *out_dir*.
    Returns the resolved absolute Path on success.
    """
    if not is_safe_relative_path(rel):
        raise ValueError(f"Unsafe relative path rejected: {rel!r}")

    root = out_dir.resolve()
    target = (out_dir / rel).resolve()

    # target == root is allowed only if rel is empty, which we already reject.
    # Otherwise target must be a proper descendant of root.
    if target != root and root not in target.parents:
        raise ValueError(
            f"Path escapes output directory: {rel!r} resolves outside {root}"
        )
    return target


def _path_is_under_root(path: Path, root: Path) -> bool:
    """True if *path* is *root* or a descendant of *root* (both should be resolved)."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def check_no_symlink_escape(out_dir: Path, rel: str) -> Path:
    """Ensure writing *rel* under *out_dir* cannot escape via symlinks.

    Walks each path component from the output root toward the target. If any
    existing component is a symlink, its resolved target must stay under
    *out_dir*. Refuses to overwrite an existing symlink at the final path.

    Returns the final absolute path (same as ensure_within_output_root).
    """
    target = ensure_within_output_root(out_dir, rel)
    root = out_dir.resolve()

    # Rebuild path component by component from root.
    # PurePosixPath keeps forward-slash semantics for the relative parts.
    rel_parts = PurePosixPath(rel).parts
    current = root
    for part in rel_parts:
        candidate = current / part
        if candidate.is_symlink():
            resolved = candidate.resolve()
            if not _path_is_under_root(resolved, root):
                raise ValueError(
                    f"Symlink escapes output directory: {candidate} -> {resolved}"
                )
            # Follow for further checks only if still inside root.
            current = resolved
        elif candidate.exists():
            current = candidate.resolve()
            if not _path_is_under_root(current, root):
                raise ValueError(
                    f"Path component resolves outside output directory: {candidate}"
                )
        else:
            # Remaining components do not exist yet; parent chain is safe.
            current = candidate
            # Do not resolve non-existent paths further.
            break

    # Final target must not already be a symlink pointing outside.
    if target.is_symlink():
        resolved = target.resolve()
        if not _path_is_under_root(resolved, root):
            raise ValueError(
                f"Refusing to overwrite symlink that escapes output directory: "
                f"{target} -> {resolved}"
            )
        raise ValueError(
            f"Refusing to overwrite existing symlink at output path: {target}"
        )

    return target


def safe_write_text(out_dir: Path, rel: str, content: str, encoding: str = "utf-8") -> Path:
    """Create parent dirs and write *content* under *out_dir* with path + symlink checks.

    On POSIX, opens the final path with O_NOFOLLOW when available so a symlink
    race cannot redirect the write outside the output root.
    """
    target = check_no_symlink_escape(out_dir, rel)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Re-check parent after mkdir (TOCTOU: parent might have been replaced).
    parent = target.parent.resolve()
    root = out_dir.resolve()
    if not _path_is_under_root(parent, root):
        raise ValueError(f"Parent directory escaped output root: {parent}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    try:
        fd = os.open(str(target), flags, 0o644)
    except OSError as e:
        if target.is_symlink():
            raise ValueError(
                f"Refusing to write through symlink at output path: {target}"
            ) from e
        raise
    # os.fdopen takes ownership of fd; close via the file object only.
    with os.fdopen(fd, "w", encoding=encoding) as f:
        f.write(content)
    return target


def validate_zip_entry_name(name: str) -> str:
    """Validate a ZIP entry name before writing.

    Same rules as relative filesystem paths; rejects traversal and absolute names.
    """
    if not is_safe_relative_path(name):
        raise ValueError(f"Unsafe ZIP entry name rejected: {name!r}")
    return name


def assert_generated_paths_safe(files: dict[str, str]) -> None:
    """Validate every key in a generate_datapack() result map."""
    for rel in files:
        if not is_safe_relative_path(rel):
            raise ValueError(f"Generated path is unsafe: {rel!r}")


def assert_generated_size_limits(files: dict[str, str]) -> None:
    """Reject generated output that is excessively large (entry count or bytes)."""
    n = len(files)
    if n > MAX_GENERATED_FILES:
        raise ValueError(
            f"Generated datapack has too many files ({n} > {MAX_GENERATED_FILES})"
        )
    total = 0
    for content in files.values():
        if not isinstance(content, str):
            raise ValueError("Generated file content must be a string")
        total += len(content.encode("utf-8"))
        if total > MAX_GENERATED_TOTAL_BYTES:
            raise ValueError(
                f"Generated datapack exceeds size limit "
                f"({total} > {MAX_GENERATED_TOTAL_BYTES} bytes)"
            )


def check_json_structure(
    obj: Any,
    *,
    max_depth: int = MAX_JSON_DEPTH,
    max_nodes: int = MAX_JSON_NODES,
) -> None:
    """Walk a parsed JSON value and reject excessive depth or node count.

    Protects against deeply nested or extremely wide JSON that would waste
    CPU/memory during menu loading and generation.
    """
    nodes = 0

    def walk(value: Any, depth: int) -> None:
        nonlocal nodes
        if depth > max_depth:
            raise ValueError(
                f"JSON nesting too deep (max depth {max_depth})"
            )
        nodes += 1
        if nodes > max_nodes:
            raise ValueError(
                f"JSON too large (max {max_nodes} nodes)"
            )
        if isinstance(value, dict):
            for k, v in value.items():
                if not isinstance(k, str):
                    raise ValueError("JSON object keys must be strings")
                nodes += 1
                if nodes > max_nodes:
                    raise ValueError(
                        f"JSON too large (max {max_nodes} nodes)"
                    )
                walk(v, depth + 1)
        elif isinstance(value, list):
            for item in value:
                walk(item, depth + 1)

    walk(obj, 1)
