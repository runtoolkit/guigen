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


def item_air_command(selector: str, slot: int) -> str:
    return f"item replace entity {selector} container.{slot} with minecraft:air"


def _custom_data_predicate(fields: dict[str, str | int]) -> str:
    """Partial-match on custom_data (works across 1.20.5–26.x)."""
    inner = ",".join(
        f'{k}:"{v}"' if isinstance(v, str) else f"{k}:{v}"
        for k, v in fields.items()
    )
    # Prefer un-namespaced custom_data key — more reliable in clear predicates.
    return f"*[custom_data~{{guigen:{{{inner}}}}}]"


def clear_by_type_id(widget_type: str, widget_id: str, count: int | None = 1) -> str:
    """Clear GUI items by widget type + id (item id does not matter)."""
    spec = _custom_data_predicate({"type": widget_type, "id": widget_id})
    if count is None:
        return f"clear @s {spec}"
    return f"clear @s {spec} {count}"


def clear_by_type(widget_type: str) -> str:
    """Clear every GUI item of a widget type."""
    spec = _custom_data_predicate({"type": widget_type})
    return f"clear @s {spec}"


def clear_all_widgets() -> str:
    """Vacuum every GUI widget item (opener book has no widget:1)."""
    return "clear @s *[custom_data~{guigen:{widget:1}}]"
