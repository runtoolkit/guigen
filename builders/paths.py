"""Output path helpers for the generated datapack.

Layout:

  data/<namespace>/function/
    core/
      load.mcfunction
      tick.mcfunction
    menu/<menu_id>/
      open.mcfunction
      close.mcfunction
      fill.mcfunction
      give_opener.mcfunction
      page/
        0.mcfunction
        1.mcfunction
      click/
        heal.mcfunction
        ...
  data/minecraft/tags/function/
    load.json
    tick.json
"""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu


def datapack_root(out_dir: Path, menu: Menu) -> Path:
    return out_dir


def ns_functions(out_dir: Path, menu: Menu) -> Path:
    return out_dir / "data" / menu.namespace / "function"


def core_dir(out_dir: Path, menu: Menu) -> Path:
    return ns_functions(out_dir, menu) / "core"


def menu_dir(out_dir: Path, menu: Menu) -> Path:
    return ns_functions(out_dir, menu) / "menu" / menu.menu_id


def page_dir(out_dir: Path, menu: Menu) -> Path:
    return menu_dir(out_dir, menu) / "page"


def click_dir(out_dir: Path, menu: Menu) -> Path:
    return menu_dir(out_dir, menu) / "click"


def tags_dir(out_dir: Path) -> Path:
    return out_dir / "data" / "minecraft" / "tags" / "function"


def ensure_dirs(out_dir: Path, menu: Menu) -> None:
    """Create required directories and remove stale generated files."""
    for d in (
        core_dir(out_dir, menu),
        menu_dir(out_dir, menu),
        page_dir(out_dir, menu),
        click_dir(out_dir, menu),
        tags_dir(out_dir),
    ):
        d.mkdir(parents=True, exist_ok=True)

    # Wipe previous generation under this menu + core so removed widgets leave no ghosts.
    for folder in (menu_dir(out_dir, menu), core_dir(out_dir, menu)):
        for f in folder.rglob("*.mcfunction"):
            f.unlink(missing_ok=True)
    # Remove legacy flat load/tick left at function root from older generator versions.
    ns = ns_functions(out_dir, menu)
    for name in ("load.mcfunction", "tick.mcfunction"):
        (ns / name).unlink(missing_ok=True)
