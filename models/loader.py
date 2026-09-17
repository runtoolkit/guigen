"""
Load a Menu from a JSON config file.

Schema (abbreviated):

{
  "namespace": "guigen",
  "menu_id": "test_menu",
  "display_name": "My Menu",
  "timer_ticks": 900,
  "follow": true,
  "distance_close": 32,
  "container": { "type": "chest_minecart" },
  "extra_scores": ["guigen_level"],
  "pages": [
    {
      "index": 0,
      "name": "Main",
      "widgets": [
        {
          "kind": "button",
          "slot": 2,
          "item": "minecraft:golden_apple",
          "action_id": "heal",
          "name": { "text": "Heal", "color": "green", "bold": true },
          "lore": [{ "text": "Restore HP", "color": "gray" }],
          "commands": ["effect give @s minecraft:instant_health 1 10 true"],
          "functions": ["mypack:extra/heal"],
          "sound": "minecraft:entity.player.levelup",
          "success_message": { "text": "Healed!", "color": "green" },
          "condition": {
            "type": "item_count_lt",
            "item": "minecraft:diamond",
            "max_count": 5,
            "fail_message": { "text": "Denied", "color": "red" }
          }
        }
      ]
    }
  ]
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .components import Text
from .menu import Container, ContainerType, Menu, Page
from .widgets import (
    Condition,
    ConditionType,
    ToggleState,
    Widget,
    WidgetKind,
)


def _text(raw: Any) -> Text | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return Text(raw)
    if isinstance(raw, dict):
        return Text(
            text=str(raw.get("text", "")),
            italic=bool(raw.get("italic", False)),
            color=raw.get("color"),
            bold=raw.get("bold"),
            underlined=raw.get("underlined"),
        )
    raise TypeError(f"Invalid text value: {raw!r}")


def _text_list(raw: Any) -> list[Text]:
    if not raw:
        return []
    if not isinstance(raw, list):
        raise TypeError(f"lore must be a list, got {type(raw)}")
    out: list[Text] = []
    for item in raw:
        t = _text(item)
        if t is not None:
            out.append(t)
    return out


def _condition(raw: Any) -> Condition | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise TypeError("condition must be an object")
    ctype = raw.get("type")
    if ctype not in (
        "item_count_lt",
        "item_count_gte",
        "score",
        "has_tag",
        "gamemode",
    ):
        raise ValueError(f"Unknown condition type: {ctype!r}")
    return Condition(
        type=ctype,  # type: ignore[arg-type]
        item=raw.get("item"),
        max_count=raw.get("max_count"),
        min_count=raw.get("min_count"),
        score=raw.get("score"),
        matches=raw.get("matches"),
        tag=raw.get("tag"),
        gamemode=raw.get("gamemode"),
        fail_message=_text(raw.get("fail_message")),
    )


def _toggle_state(raw: Any) -> ToggleState:
    if not isinstance(raw, dict):
        raise TypeError("toggle must be an object")
    for key in ("score", "off_item", "on_item", "off_name", "on_name"):
        if key not in raw:
            raise ValueError(f"toggle missing required field: {key}")
    off_name = _text(raw["off_name"])
    on_name = _text(raw["on_name"])
    assert off_name is not None and on_name is not None
    return ToggleState(
        score=str(raw["score"]),
        off_item=str(raw["off_item"]),
        on_item=str(raw["on_item"]),
        off_name=off_name,
        on_name=on_name,
        off_lore=_text_list(raw.get("off_lore")),
        on_lore=_text_list(raw.get("on_lore")),
        on_commands=list(raw.get("on_commands") or []),
        off_commands=list(raw.get("off_commands") or []),
        tick_while_on=list(raw.get("tick_while_on") or []),
    )


def _widget(raw: Any) -> Widget:
    if not isinstance(raw, dict):
        raise TypeError("widget must be an object")
    kind = raw.get("kind") or raw.get("type")
    if not kind:
        raise ValueError("widget requires 'kind'")
    # aliases
    aliases = {
        "btn": "button",
        "sep": "separator",
        "filler": "separator",
        "pad": "separator",
        "close_btn": "close",
        "navigation": "nav",
        "page": "nav",
        "bar": "progress",
        "stepper": "counter",
    }
    kind = aliases.get(str(kind), str(kind))
    valid: tuple[str, ...] = (
        "button",
        "label",
        "separator",
        "toggle",
        "counter",
        "nav",
        "progress",
        "close",
        "confirm",
    )
    if kind not in valid:
        raise ValueError(f"Unknown widget kind: {kind!r} (allowed: {', '.join(valid)})")

    if "slot" not in raw and kind != "progress":
        raise ValueError(f"widget kind={kind} requires 'slot'")
    slot = int(raw.get("slot", raw.get("start_slot", 0)))

    clickable = True
    if kind in ("label", "separator", "progress"):
        clickable = False
    if "clickable" in raw:
        clickable = bool(raw["clickable"])

    w = Widget(
        slot=slot,
        kind=kind,  # type: ignore[arg-type]
        item=str(raw.get("item", "minecraft:stone")),
        action_id=str(raw.get("action_id") or raw.get("id") or ""),
        name=_text(raw.get("name")),
        lore=_text_list(raw.get("lore")),
        commands=list(raw.get("commands") or []),
        functions=list(raw.get("functions") or []),
        sound=raw.get("sound"),
        success_message=_text(raw.get("success_message")),
        condition=_condition(raw.get("condition")),
        target_page=raw.get("target_page"),
        confirm_page=raw.get("confirm_page"),
        counter_score=raw.get("counter_score") or raw.get("score"),
        counter_delta=int(raw.get("counter_delta") or raw.get("delta") or 1),
        counter_min=int(raw.get("counter_min") or raw.get("min") or raw.get("min_v") or 0),
        counter_max=int(raw.get("counter_max") or raw.get("max") or raw.get("max_v") or 64),
        progress_score=raw.get("progress_score") or (
            raw.get("score") if kind == "progress" else None
        ),
        progress_max=int(raw.get("progress_max") or raw.get("max") or raw.get("max_v") or 10),
        progress_width=int(raw.get("progress_width") or raw.get("width") or 5),
        progress_full_item=str(
            raw.get("progress_full_item") or raw.get("full_item") or "minecraft:lime_stained_glass_pane"
        ),
        progress_empty_item=str(
            raw.get("progress_empty_item")
            or raw.get("empty_item")
            or "minecraft:gray_stained_glass_pane"
        ),
        clickable=clickable,
    )

    if kind == "toggle":
        if "toggle" not in raw:
            raise ValueError("toggle widget requires 'toggle' object")
        w.toggle = _toggle_state(raw["toggle"])
        if not w.item or w.item == "minecraft:stone":
            w.item = w.toggle.off_item
        if w.name is None:
            w.name = w.toggle.off_name
        if not w.action_id:
            w.action_id = w.toggle.score

    if kind == "nav" and w.target_page is None:
        raise ValueError("nav widget requires target_page")
    if kind == "confirm" and w.confirm_page is None:
        raise ValueError("confirm widget requires confirm_page")
    if kind == "counter" and not w.counter_score:
        raise ValueError("counter widget requires score / counter_score")
    if kind == "progress" and not w.progress_score:
        raise ValueError("progress widget requires score / progress_score")
    if kind == "close" and not w.action_id:
        w.action_id = "close_menu"
        if w.name is None:
            w.name = Text("Close Menu", color="red")
        if not w.lore:
            w.lore = [Text("Close this menu", color="gray")]
        if w.item == "minecraft:stone":
            w.item = "minecraft:barrier"
        if w.success_message is None:
            w.success_message = Text("Menu closed.", color="red")
    if kind == "separator":
        if not w.action_id:
            w.action_id = f"separator_{slot}"
        if w.name is None:
            w.name = Text(" ", color="dark_gray")
        if w.item == "minecraft:stone":
            w.item = "minecraft:gray_stained_glass_pane"

    return w


def _page(raw: Any, fallback_index: int) -> Page:
    if not isinstance(raw, dict):
        raise TypeError("page must be an object")
    index = int(raw.get("index", fallback_index))
    name = str(raw.get("name", f"Page {index}"))
    widgets_raw = raw.get("widgets") or raw.get("buttons") or []
    if not isinstance(widgets_raw, list):
        raise TypeError("page.widgets must be a list")
    widgets = [_widget(w) for w in widgets_raw]
    return Page(index=index, name=name, widgets=widgets)


def _container(raw: Any) -> Container:
    if raw is None:
        return Container()
    if not isinstance(raw, dict):
        raise TypeError("container must be an object")
    ctype = str(raw.get("type", "chest_minecart"))
    if ctype not in ("chest_minecart", "hopper_minecart"):
        raise ValueError(
            f"Unknown container type: {ctype!r} "
            "(allowed: chest_minecart, hopper_minecart)"
        )
    return Container(
        type=ctype,  # type: ignore[arg-type]
        invulnerable=bool(raw.get("invulnerable", True)),
        no_gravity=bool(raw.get("no_gravity", True)),
        silent=bool(raw.get("silent", True)),
    )


def menu_from_dict(data: dict[str, Any]) -> Menu:
    if "namespace" not in data or "menu_id" not in data:
        raise ValueError("config requires 'namespace' and 'menu_id'")
    pages_raw = data.get("pages") or []
    if not isinstance(pages_raw, list) or not pages_raw:
        raise ValueError("config requires non-empty 'pages' list")
    pages = [_page(p, i) for i, p in enumerate(pages_raw)]

    return Menu(
        namespace=str(data["namespace"]),
        menu_id=str(data["menu_id"]),
        display_name=str(data.get("display_name", data["menu_id"])),
        timer_ticks=int(data.get("timer_ticks", 900)),
        follow=bool(data.get("follow", True)),
        distance_close=float(data.get("distance_close", 32)),
        container=_container(data.get("container")),
        pages=pages,
        extra_scores=list(data.get("extra_scores") or []),
        pack_description=data.get("pack_description"),
        opener_name=data.get("opener_name"),
        opener_lore=data.get("opener_lore"),
    )


def load_menu(path: str | Path) -> Menu:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError("JSON root must be an object")
    return menu_from_dict(data)
