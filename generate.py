#!/usr/bin/env python3
"""
GUI Generator – entry point.

Builds a complete Minecraft datapack from a declarative Menu definition.
Item names / lore are emitted as SNBT *objects*, never as stringified JSON.

Usage:
  python generate.py
  python generate.py --out ./my_output
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# allow running from the gui_generator directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.test_menu import build_test_menu
from builders.paths import ensure_dirs
from generators import (
    generate_fill_router,
    generate_page_fills,
    generate_handlers,
    generate_tick,
    generate_load,
    generate_open,
    generate_close,
    generate_give_opener,
    generate_tags,
    generate_pack_mcmeta,
)


def generate(out_dir: Path) -> None:
    menu = build_test_menu()
    ensure_dirs(out_dir, menu)

    generate_load(menu, out_dir)
    generate_open(menu, out_dir)
    generate_close(menu, out_dir)
    generate_give_opener(menu, out_dir)
    generate_fill_router(menu, out_dir)
    generate_page_fills(menu, out_dir)
    generate_handlers(menu, out_dir)
    generate_tick(menu, out_dir)
    generate_tags(menu, out_dir)
    generate_pack_mcmeta(
        out_dir,
        description=f"GUI-GENERATOR – {menu.display_name} (pages, toggles, conditions)",
    )

    print(f"Generated datapack at: {out_dir.resolve()}")
    print(f"  namespace : {menu.namespace}")
    print(f"  menu     : {menu.menu_id}")
    print(f"  pages    : {len(menu.pages)}")
    print(f"  buttons  : {len(menu.all_buttons())}")
    print(f"Open with : /function {menu.function_prefix}/open")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GUI datapack from config")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "datapack",
        help="Output directory for the datapack",
    )
    args = parser.parse_args()
    generate(args.out)


if __name__ == "__main__":
    main()
