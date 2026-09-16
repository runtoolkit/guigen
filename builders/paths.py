"""Output path helpers for the generated datapack."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu


def datapack_root(out_dir: Path, menu: Menu) -> Path:
    return out_dir


def ns_functions(out_dir: Path, menu: Menu) -> Path:
    return out_dir / "data" / menu.namespace / "function"


def menu_dir(out_dir: Path, menu: Menu) -> Path:
    return ns_functions(out_dir, menu) / "menu" / menu.menu_id


def tags_dir(out_dir: Path) -> Path:
    return out_dir / "data" / "minecraft" / "tags" / "function"


def ensure_dirs(out_dir: Path, menu: Menu) -> None:
    """Create required directories and remove stale generated files from previous runs."""
    mdir = menu_dir(out_dir, menu)
    mdir.mkdir(parents=True, exist_ok=True)
    tags_dir(out_dir).mkdir(parents=True, exist_ok=True)

    # Clear old .mcfunction files in the menu folder so removed widgets/actions
    # (and their on_click_*, fill_page* etc.) do not linger after regeneration.
    for f in mdir.glob("*.mcfunction"):
        f.unlink(missing_ok=True)
