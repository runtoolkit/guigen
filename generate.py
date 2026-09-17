#!/usr/bin/env python3
"""
GUI Generator – entry point.

Builds a complete Minecraft datapack from a JSON menu config.

Usage:
  python generate.py
  python generate.py --config config/test_menu.json
  python generate.py --config ./my_menu.json --out ./my_output
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.loader import load_menu
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


DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "test_menu.json"


def generate(config_path: Path, out_dir: Path) -> None:
    menu = load_menu(config_path)
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
        description=menu.pack_description
        or f"GUI-GENERATOR – {menu.display_name}",
    )

    print(f"Config    : {config_path.resolve()}")
    print(f"Generated : {out_dir.resolve()}")
    print(f"  namespace : {menu.namespace}")
    print(f"  menu     : {menu.menu_id}")
    print(f"  pages    : {len(menu.pages)}")
    print(f"  widgets  : {len(menu.all_widgets())}")
    print(f"  container: {menu.container.type} ({menu.container.slot_count} slots)")
    print(f"Open with : /function {menu.function_prefix}/open")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Minecraft GUI datapack from a JSON config"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Path to menu JSON (default: {DEFAULT_CONFIG.name})",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "datapack",
        help="Output directory for the datapack",
    )
    args = parser.parse_args()
    generate(args.config, args.out)


if __name__ == "__main__":
    main()
