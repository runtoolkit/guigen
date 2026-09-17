"""SNBT / item component helpers (port of components.py + builders/snbt.py)."""

from __future__ import annotations

from typing import Any


def escape_snbt_string(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def mk_text(
    text: str | None = "",
    *,
    italic: bool = False,
    color: str | None = None,
    bold: bool | None = None,
    underlined: bool | None = None,
) -> dict[str, Any]:
    return {
        "text": "" if text is None else str(text),
        "italic": bool(italic),
        "color": color,
        "bold": bold,
        "underlined": underlined,
    }


def text_to_snbt(t: dict[str, Any]) -> str:
    parts = [f'text:"{escape_snbt_string(t["text"])}"']
    parts.append(f"italic:{str(bool(t.get('italic'))).lower()}")
    if t.get("color") is not None:
        parts.append(f'color:"{t["color"]}"')
    if t.get("bold") is not None:
        parts.append(f"bold:{'true' if t['bold'] else 'false'}")
    if t.get("underlined") is not None:
        parts.append(f"underlined:{'true' if t['underlined'] else 'false'}")
    return "{" + ",".join(parts) + "}"


def value_to_snbt(v: Any) -> str:
    if isinstance(v, bool):
        return "1b" if v else "0b"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"{v}d"
    if isinstance(v, str):
        return f'"{escape_snbt_string(v)}"'
    if isinstance(v, list):
        return "[" + ",".join(value_to_snbt(x) for x in v) + "]"
    if isinstance(v, dict):
        return dict_to_snbt(v)
    raise TypeError(f"Unsupported SNBT value type: {type(v).__name__}")


def dict_to_snbt(d: dict[str, Any]) -> str:
    items = [f"{k}:{value_to_snbt(v)}" for k, v in d.items()]
    return "{" + ",".join(items) + "}"


def mk_item_components(
    *,
    custom_name: dict[str, Any] | None = None,
    lore: list[dict[str, Any]] | None = None,
    custom_data: dict[str, Any] | None = None,
    max_stack_size: int = 1,
) -> dict[str, Any]:
    return {
        "custom_name": custom_name,
        "lore": list(lore or []),
        "custom_data": dict(custom_data or {}),
        "max_stack_size": max_stack_size,
    }


def item_components_to_snbt_suffix(c: dict[str, Any]) -> str:
    parts: list[str] = []
    if c.get("custom_name") is not None:
        parts.append(f"custom_name={text_to_snbt(c['custom_name'])}")
    lore = c.get("lore") or []
    if lore:
        lore_snbt = "[" + ",".join(text_to_snbt(t) for t in lore) + "]"
        parts.append(f"lore={lore_snbt}")
    custom_data = c.get("custom_data") or {}
    if custom_data:
        parts.append(f"custom_data={dict_to_snbt(custom_data)}")
    if c.get("max_stack_size", 64) != 64:
        parts.append(f"max_stack_size={c['max_stack_size']}")
    if not parts:
        return ""
    return "[" + ",".join(parts) + "]"


def item_id(item: str) -> str:
    return item if ":" in item else f"minecraft:{item}"


def item_replace_command(selector: str, slot: int, item: str, components: dict[str, Any]) -> str:
    suffix = item_components_to_snbt_suffix(components)
    return f"item replace entity {selector} container.{slot} with {item_id(item)}{suffix}"


def item_air_command(selector: str, slot: int) -> str:
    return f"item replace entity {selector} container.{slot} with minecraft:air"


def custom_data_predicate(fields: dict[str, Any]) -> str:
    inner_parts = []
    for k, v in fields.items():
        if isinstance(v, str):
            inner_parts.append(f'{k}:"{v}"')
        else:
            inner_parts.append(f"{k}:{v}")
    inner = ",".join(inner_parts)
    return f"*[custom_data~{{guigenmc:{{{inner}}}}}]"


def clear_by_type_id(widget_type: str, widget_id: str, count: int | None = 1) -> str:
    spec = custom_data_predicate({"type": widget_type, "id": widget_id})
    if count is None:
        return f"clear @s {spec}"
    return f"clear @s {spec} {count}"


def clear_by_type(widget_type: str) -> str:
    spec = custom_data_predicate({"type": widget_type})
    return f"clear @s {spec}"


def clear_all_widgets() -> str:
    return "clear @s *[custom_data~{guigenmc:{widget:1}}]"
