"""Emit item replace / clear commands with object-style components."""

from __future__ import annotations

from models.components import ItemComponents


def item_id(item: str) -> str:
    return item if ":" in item else f"minecraft:{item}"


def item_replace_command(selector: str, slot: int, item: str, components: ItemComponents) -> str:
    suffix = components.to_snbt_suffix()
    return (
        f"item replace entity {selector} container.{slot} "
        f"with {item_id(item)}{suffix}"
    )


def clear_detect_command(item: str, action: str) -> str:
    return (
        f'clear @s {item_id(item)}'
        f'[custom_data={{guigen:{{action:"{action}"}}}}] 1'
    )
