"""Path and identifier safety helpers for datapack generation.

Minecraft datapack identifiers (namespace, function path segments, etc.)
follow a restricted character set. User-controlled values that end up in
filesystem or ZIP paths must be validated before use.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

# Minecraft resource location path segment (namespace / path parts):
# lowercase a-z, 0-9, underscore, hyphen, period. No slashes or spaces.
# See: https://minecraft.wiki/w/Resource_location
_IDENTIFIER_RE = re.compile(r"^[a-z0-9._-]+$")

# Characters that must never appear in a relative path we write.
_UNSAFE_PATH_CHARS = ("\x00", "\\", "..")


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
