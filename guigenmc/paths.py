"""Path helpers for datapack file layout."""

from __future__ import annotations

from typing import Any


def ns_functions_path(menu: dict[str, Any]) -> str:
    return f"data/{menu['namespace']}/function"


def core_dir_path(menu: dict[str, Any]) -> str:
    return f"{ns_functions_path(menu)}/core"


def menu_dir_path(menu: dict[str, Any]) -> str:
    return f"{ns_functions_path(menu)}/menu/{menu['menu_id']}"


def page_dir_path(menu: dict[str, Any]) -> str:
    return f"{menu_dir_path(menu)}/page"


def click_dir_path(menu: dict[str, Any]) -> str:
    return f"{menu_dir_path(menu)}/click"
