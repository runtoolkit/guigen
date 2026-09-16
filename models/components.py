"""
Text components and item component models.
Names / lore are stored as objects (dicts), never as pre-stringified JSON.
When emitted they become SNBT objects: {text:"...",italic:false,color:"aqua"}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Text:
    """A single Minecraft text component as a real object."""
    text: str
    italic: bool = False
    color: str | None = None
    bold: bool | None = None
    underlined: bool | None = None

    def to_snbt(self) -> str:
        parts = [f'text:"{_escape(self.text)}"']
        parts.append(f"italic:{str(self.italic).lower()}")
        if self.color is not None:
            parts.append(f'color:"{self.color}"')
        if self.bold is not None:
            parts.append(f"bold:{str(self.bold).lower()}")
        if self.underlined is not None:
            parts.append(f"underlined:{str(self.underlined).lower()}")
        return "{" + ",".join(parts) + "}"


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


@dataclass
class ItemComponents:
    """
    Item components written as SNBT objects, not stringified JSON.
    custom_name -> object
    lore        -> list of objects
    custom_data -> nested object
    """
    custom_name: Text | None = None
    lore: list[Text] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)

    def to_snbt_suffix(self) -> str:
        """Returns the [component=...,component=...] part (without brackets if empty)."""
        parts: list[str] = []
        if self.custom_name is not None:
            parts.append(f"custom_name={self.custom_name.to_snbt()}")
        if self.lore:
            lore_snbt = "[" + ",".join(t.to_snbt() for t in self.lore) + "]"
            parts.append(f"lore={lore_snbt}")
        if self.custom_data:
            parts.append(f"custom_data={_dict_to_snbt(self.custom_data)}")
        if not parts:
            return ""
        return "[" + ",".join(parts) + "]"


def _dict_to_snbt(d: dict[str, Any]) -> str:
    """Recursively convert a Python dict into SNBT compound."""
    items = []
    for k, v in d.items():
        items.append(f"{k}:{_value_to_snbt(v)}")
    return "{" + ",".join(items) + "}"


def _value_to_snbt(v: Any) -> str:
    if isinstance(v, bool):
        return "1b" if v else "0b"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"{v}d"
    if isinstance(v, str):
        return f'"{_escape(v)}"'
    if isinstance(v, dict):
        return _dict_to_snbt(v)
    if isinstance(v, list):
        return "[" + ",".join(_value_to_snbt(x) for x in v) + "]"
    raise TypeError(f"Unsupported SNBT value type: {type(v)}")
