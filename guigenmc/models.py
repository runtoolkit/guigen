"""Menu / widget models and JSON loader (port of models/)."""

from __future__ import annotations

import json
from typing import Any

from .components import mk_text

# ---------------------------------------------------------------------------
# Widget helpers
# ---------------------------------------------------------------------------

VALID_WIDGET_KINDS = [
    "button",
    "label",
    "separator",
    "toggle",
    "counter",
    "nav",
    "progress",
    "close",
    "confirm",
    "random",
]

WIDGET_KIND_ALIASES = {
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

VALID_CONDITION_TYPES = ["item_count_lt", "item_count_gte", "score", "has_tag", "gamemode"]


def resolved_action_id(w: dict[str, Any]) -> str:
    if w.get("action_id"):
        return str(w["action_id"])
    return f"{w['kind']}_{w['slot']}"


def occupied_slots(w: dict[str, Any]) -> list[int]:
    if w["kind"] == "progress":
        width = max(1, int(w.get("progress_width") or 1))
        return [w["slot"] + i for i in range(width)]
    return [w["slot"]]


def gui_custom_data(w: dict[str, Any], cell_slot: int | None = None) -> dict[str, Any]:
    wid = resolved_action_id(w)
    if cell_slot is not None:
        wid = f"{wid}_s{cell_slot}"
    return {"guigen": {"widget": 1, "type": w["kind"], "id": wid}}


def widget_components(w: dict[str, Any], cell_slot: int | None = None) -> dict[str, Any]:
    from .components import mk_item_components

    return mk_item_components(
        custom_name=w.get("name"),
        lore=list(w.get("lore") or []),
        custom_data=gui_custom_data(w, cell_slot),
    )


def components_for_toggle(w: dict[str, Any], state: int) -> tuple[str, dict[str, Any]]:
    from .components import mk_item_components

    t = w["toggle"]
    data = gui_custom_data(w)
    if state == 0:
        return (
            t["off_item"],
            mk_item_components(
                custom_name=t["off_name"],
                lore=list(t.get("off_lore") or []),
                custom_data=data,
            ),
        )
    return (
        t["on_item"],
        mk_item_components(
            custom_name=t["on_name"],
            lore=list(t.get("on_lore") or []),
            custom_data=data,
        ),
    )


def is_interactive(w: dict[str, Any]) -> bool:
    return w["kind"] not in ("label", "separator", "progress")


def mk_separator_widget(slot: int, item: str = "minecraft:gray_stained_glass_pane") -> dict[str, Any]:
    return mk_widget(
        slot=slot,
        kind="separator",
        item=item,
        action_id=f"separator_{slot}",
        name=mk_text(" ", color="dark_gray"),
        clickable=False,
    )


def mk_widget(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "slot": 0,
        "kind": "button",
        "item": "minecraft:stone",
        "action_id": "",
        "name": None,
        "lore": [],
        "commands": [],
        "functions": [],
        "sound": None,
        "success_message": None,
        "condition": None,
        "cooldown_ticks": 0,
        "cost": None,
        "toggle": None,
        "target_page": None,
        "confirm_page": None,
        "counter_score": None,
        "counter_delta": 1,
        "counter_min": 0,
        "counter_max": 64,
        "counter_wrap": False,
        "counter_display_item": None,
        "progress_score": None,
        "progress_max": 10,
        "progress_width": 5,
        "progress_full_item": "minecraft:lime_stained_glass_pane",
        "progress_empty_item": "minecraft:gray_stained_glass_pane",
        "random": None,
        "clickable": True,
    }
    base.update(fields)
    return base


# ---------------------------------------------------------------------------
# Container / menu helpers
# ---------------------------------------------------------------------------


def mk_container(
    *,
    type: str = "chest_minecart",
    invulnerable: bool = True,
    no_gravity: bool = True,
    silent: bool = True,
) -> dict[str, Any]:
    return {
        "type": type,
        "invulnerable": invulnerable,
        "no_gravity": no_gravity,
        "silent": silent,
    }


def container_entity_id(c: dict[str, Any]) -> str:
    return f"minecraft:{c['type']}"


def container_slot_count(c: dict[str, Any]) -> int:
    return 5 if c["type"] == "hopper_minecart" else 27


def container_summon_nbt(
    c: dict[str, Any], tags: list[str], custom_name: str | None = None
) -> str:
    from .components import escape_snbt_string

    tag_list = ",".join(f'"{t}"' for t in tags)
    flags: list[str] = []
    if c.get("invulnerable"):
        flags.append("Invulnerable:1b")
    if c.get("no_gravity"):
        flags.append("NoGravity:1b")
    if c.get("silent"):
        flags.append("Silent:1b")
    flags.append("CustomNameVisible:0b")
    if custom_name:
        flags.append(f'CustomName:{{text:"{escape_snbt_string(custom_name)}",italic:false}}')
    flags.append(f"Tags:[{tag_list}]")
    return "{" + ",".join(flags) + "}"


def menu_function_prefix(m: dict[str, Any]) -> str:
    return f"{m['namespace']}:menu/{m['menu_id']}"


def menu_core_prefix(m: dict[str, Any]) -> str:
    return f"{m['namespace']}:core"


def menu_page_prefix(m: dict[str, Any]) -> str:
    return f"{menu_function_prefix(m)}/page"


def menu_click_prefix(m: dict[str, Any]) -> str:
    return f"{menu_function_prefix(m)}/click"


def menu_tag(m: dict[str, Any]) -> str:
    return f"{m['namespace']}.{m['menu_id']}"


def all_widgets(m: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for p in m["pages"]:
        result.extend(p["widgets"])
    return result


def interactive_widgets(m: dict[str, Any]) -> list[dict[str, Any]]:
    return [w for w in all_widgets(m) if is_interactive(w)]


def collect_scores(m: dict[str, Any]) -> list[str]:
    scores = ["guigen_menu_timer", "guigen_click", "guigen_page", "guigen_tmp", "guigen_rand"]
    for s in m.get("extra_scores") or []:
        if s not in scores:
            scores.append(s)
    for w in all_widgets(m):
        if w.get("toggle") and w["toggle"]["score"] not in scores:
            scores.append(w["toggle"]["score"])
        if w.get("counter_score") and w["counter_score"] not in scores:
            scores.append(w["counter_score"])
        if w.get("progress_score") and w["progress_score"] not in scores:
            scores.append(w["progress_score"])
    return scores


# ---------------------------------------------------------------------------
# JSON loaders
# ---------------------------------------------------------------------------


def loader_text(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return mk_text(raw)
    if isinstance(raw, dict):
        return mk_text(
            raw.get("text", ""),
            italic=bool(raw.get("italic")),
            color=raw.get("color"),
            bold=raw.get("bold"),
            underlined=raw.get("underlined"),
        )
    raise TypeError(f"Invalid text value: {raw!r}")


def loader_text_list(raw: Any) -> list[dict[str, Any]]:
    if not raw:
        return []
    if not isinstance(raw, list):
        raise TypeError("lore must be a list")
    out: list[dict[str, Any]] = []
    for item in raw:
        t = loader_text(item)
        if t is not None:
            out.append(t)
    return out


def loader_condition(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise TypeError("condition must be an object")
    ctype = raw.get("type")
    if ctype not in VALID_CONDITION_TYPES:
        raise ValueError(f"Unknown condition type: {ctype}")
    return {
        "type": ctype,
        "item": raw.get("item"),
        "max_count": raw.get("max_count"),
        "min_count": raw.get("min_count"),
        "score": raw.get("score"),
        "matches": raw.get("matches"),
        "tag": raw.get("tag"),
        "gamemode": raw.get("gamemode"),
        "fail_message": loader_text(raw.get("fail_message")),
    }


def loader_cost(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise TypeError("cost must be an object")
    if not raw.get("item") and not raw.get("score"):
        raise ValueError("cost requires 'item' and/or 'score'")
    return {
        "item": raw.get("item"),
        "count": int(raw.get("count", 1)),
        "score": raw.get("score"),
        "amount": int(raw.get("amount", 1)),
        "fail_message": loader_text(raw.get("fail_message")),
    }


def loader_toggle_state(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("toggle must be an object")
    for key in ("score", "off_item", "on_item", "off_name", "on_name"):
        if key not in raw:
            raise ValueError(f"toggle missing required field: {key}")
    return {
        "score": str(raw["score"]),
        "off_item": str(raw["off_item"]),
        "on_item": str(raw["on_item"]),
        "off_name": loader_text(raw["off_name"]),
        "on_name": loader_text(raw["on_name"]),
        "off_lore": loader_text_list(raw.get("off_lore")),
        "on_lore": loader_text_list(raw.get("on_lore")),
        "on_commands": list(raw.get("on_commands") or []),
        "off_commands": list(raw.get("off_commands") or []),
        "tick_while_on": list(raw.get("tick_while_on") or []),
    }


def loader_random_reward(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError(f"random.rewards[{index}] must be an object")
    weight = int(raw.get("weight", 1))
    if weight <= 0:
        raise ValueError(f"random.rewards[{index}].weight must be > 0")
    return {
        "weight": weight,
        "commands": list(raw.get("commands") or []),
        "functions": list(raw.get("functions") or []),
        "message": loader_text(raw.get("message")),
    }


def loader_random(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("random must be an object")
    rewards_raw = raw.get("rewards") or []
    if not isinstance(rewards_raw, list) or not rewards_raw:
        raise ValueError("random widget requires a non-empty 'rewards' list")
    return {"rewards": [loader_random_reward(r, i) for i, r in enumerate(rewards_raw)]}


def loader_widget(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("widget must be an object")
    kind = raw.get("kind") or raw.get("type")
    if not kind:
        raise ValueError("widget requires 'kind'")
    kind = WIDGET_KIND_ALIASES.get(str(kind), str(kind))
    if kind not in VALID_WIDGET_KINDS:
        raise ValueError(f"Unknown widget kind: {kind} (allowed: {', '.join(VALID_WIDGET_KINDS)})")

    if "slot" not in raw and kind != "progress":
        raise ValueError(f"widget kind={kind} requires 'slot'")
    slot = int(raw.get("slot", raw.get("start_slot", 0)))

    clickable = True
    if kind in ("label", "separator", "progress"):
        clickable = False
    if "clickable" in raw:
        clickable = bool(raw["clickable"])

    w = mk_widget(
        slot=slot,
        kind=kind,
        item=str(raw.get("item", "minecraft:stone")),
        action_id=str(raw.get("action_id", raw.get("id", ""))),
        name=loader_text(raw.get("name")),
        lore=loader_text_list(raw.get("lore")),
        commands=list(raw.get("commands") or []),
        functions=list(raw.get("functions") or []),
        sound=raw.get("sound"),
        success_message=loader_text(raw.get("success_message")),
        condition=loader_condition(raw.get("condition")),
        cooldown_ticks=int(raw.get("cooldown_ticks", raw.get("cooldown", 0))),
        cost=loader_cost(raw.get("cost")),
        target_page=raw.get("target_page"),
        confirm_page=raw.get("confirm_page"),
        counter_score=raw.get("counter_score", raw.get("score")),
        counter_delta=int(raw.get("counter_delta", raw.get("delta", 1))),
        counter_min=int(raw.get("counter_min", raw.get("min", raw.get("min_v", 0)))),
        counter_max=int(raw.get("counter_max", raw.get("max", raw.get("max_v", 64)))),
        counter_wrap=bool(raw.get("counter_wrap", raw.get("wrap", False))),
        progress_score=raw.get("progress_score")
        if kind != "progress"
        else (raw.get("progress_score") or raw.get("score")),
        progress_max=int(raw.get("progress_max", raw.get("max", raw.get("max_v", 10)))),
        progress_width=int(raw.get("progress_width", raw.get("width", 5))),
        progress_full_item=str(
            raw.get("progress_full_item", raw.get("full_item", "minecraft:lime_stained_glass_pane"))
        ),
        progress_empty_item=str(
            raw.get("progress_empty_item", raw.get("empty_item", "minecraft:gray_stained_glass_pane"))
        ),
        clickable=clickable,
    )

    if kind == "toggle":
        if "toggle" not in raw:
            raise ValueError("toggle widget requires 'toggle' object")
        w["toggle"] = loader_toggle_state(raw["toggle"])
        if not w["item"] or w["item"] == "minecraft:stone":
            w["item"] = w["toggle"]["off_item"]
        if w["name"] is None:
            w["name"] = w["toggle"]["off_name"]
        if not w["action_id"]:
            w["action_id"] = w["toggle"]["score"]

    if kind == "random":
        if "random" not in raw:
            raise ValueError("random widget requires 'random' object")
        w["random"] = loader_random(raw["random"])

    if kind == "nav" and w["target_page"] is None:
        raise ValueError("nav widget requires target_page")
    if kind == "confirm" and w["confirm_page"] is None:
        raise ValueError("confirm widget requires confirm_page")
    if kind == "counter" and not w["counter_score"]:
        raise ValueError("counter widget requires score / counter_score")
    if kind == "progress" and not w["progress_score"]:
        raise ValueError("progress widget requires score / progress_score")

    if kind == "close" and not w["action_id"]:
        w["action_id"] = "close_menu"
        if w["name"] is None:
            w["name"] = mk_text("Close Menu", color="red")
        if not w["lore"]:
            w["lore"] = [mk_text("Close this menu", color="gray")]
        if w["item"] == "minecraft:stone":
            w["item"] = "minecraft:barrier"
        if w["success_message"] is None:
            w["success_message"] = mk_text("Menu closed.", color="red")

    if kind == "separator":
        if not w["action_id"]:
            w["action_id"] = f"separator_{slot}"
        if w["name"] is None:
            w["name"] = mk_text(" ", color="dark_gray")
        if w["item"] == "minecraft:stone":
            w["item"] = "minecraft:gray_stained_glass_pane"

    return w


def loader_page(raw: Any, fallback_index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("page must be an object")
    index = int(raw.get("index", fallback_index))
    name = str(raw.get("name", f"Page {index}"))
    widgets_raw = raw.get("widgets") or raw.get("buttons") or []
    if not isinstance(widgets_raw, list):
        raise TypeError("page.widgets must be a list")
    widgets = [loader_widget(w) for w in widgets_raw]
    return {"index": index, "name": name, "widgets": widgets}


def loader_container(raw: Any) -> dict[str, Any]:
    if raw is None:
        return mk_container()
    if not isinstance(raw, dict):
        raise TypeError("container must be an object")
    ctype = str(raw.get("type", "chest_minecart"))
    if ctype not in ("chest_minecart", "hopper_minecart"):
        raise ValueError(
            f"Unknown container type: {ctype} (allowed: chest_minecart, hopper_minecart)"
        )
    return mk_container(
        type=ctype,
        invulnerable=raw.get("invulnerable", True),
        no_gravity=raw.get("no_gravity", True),
        silent=raw.get("silent", True),
    )


def menu_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    if "namespace" not in data or "menu_id" not in data:
        raise ValueError("config requires 'namespace' and 'menu_id'")
    pages_raw = data.get("pages") or []
    if not isinstance(pages_raw, list) or not pages_raw:
        raise ValueError("config requires non-empty 'pages' list")
    pages = [loader_page(p, i) for i, p in enumerate(pages_raw)]
    return {
        "namespace": str(data["namespace"]),
        "menu_id": str(data["menu_id"]),
        "display_name": str(data.get("display_name", data["menu_id"])),
        "timer_ticks": int(data.get("timer_ticks", 900)),
        "follow": data.get("follow", True),
        "distance_close": float(data.get("distance_close", 32)),
        "container": loader_container(data.get("container")),
        "pages": pages,
        "extra_scores": list(data.get("extra_scores") or []),
        "pack_description": data.get("pack_description"),
        "opener_name": data.get("opener_name"),
        "opener_lore": data.get("opener_lore"),
    }


def load_menu_from_json_string(json_text: str) -> dict[str, Any]:
    data = json.loads(json_text)
    if not isinstance(data, dict):
        raise TypeError("JSON root must be an object")
    return menu_from_dict(data)


def load_menu_from_file(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return load_menu_from_json_string(f.read())
