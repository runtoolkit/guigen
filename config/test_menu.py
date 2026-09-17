"""Backward-compatible Python entry that loads config/test_menu.json."""

from __future__ import annotations
from pathlib import Path

from models.loader import load_menu
from models.menu import Menu


def build_test_menu() -> Menu:
    return load_menu(Path(__file__).with_name("test_menu.json"))
