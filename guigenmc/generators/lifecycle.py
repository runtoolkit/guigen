"""Load / open / close / opener / tags / pack.mcmeta generators."""

from __future__ import annotations

import json
from typing import Any

from ..components import clear_all_widgets, item_air_command
from ..models import (
    all_widgets,
    collect_scores,
    container_entity_id,
    container_slot_count,
    container_summon_nbt,
    interactive_widgets,
    menu_core_prefix,
    menu_function_prefix,
    menu_tag,
    resolved_action_id,
)
from ..paths import core_dir_path, menu_dir_path
from .handlers import cd_score


def generate_load(menu: dict[str, Any], out: dict[str, str]) -> None:
    lines = ["# Auto-generated core load"]
    scores = list(collect_scores(menu))
    for w in interactive_widgets(menu):
        if int(w.get("cooldown_ticks") or 0) > 0:
            sc = cd_score(resolved_action_id(w))
            if sc not in scores:
                scores.append(sc)

    for score in scores:
        lines.append(f"scoreboard objectives add {score} dummy")
    cart = f"@e[type={container_entity_id(menu['container'])},tag={menu_tag(menu)}]"
    lines.extend(
        [
            "",
            f"execute as {cart} run data modify entity @s Items set value []",
            f"kill {cart}",
            "",
            f'tellraw @a [{{"text":"[GUI-GENERATOR] ","color":"gray"}},'
            f'{{"text":"Loaded. /function {menu_function_prefix(menu)}/open","color":"green"}}]',
            "",
        ]
    )
    out[f"{core_dir_path(menu)}/load.mcfunction"] = "\n".join(lines)


def generate_open(menu: dict[str, Any], out: dict[str, str]) -> None:
    nbt = container_summon_nbt(
        menu["container"],
        [f"{menu['namespace']}.menu", menu_tag(menu)],
        menu["display_name"],
    )
    y_off = float(menu["container"].get("y_offset") or 0.0)
    if y_off:
        summon_coords = f"~ ~{y_off} ~"
    else:
        summon_coords = "~ ~ ~"
    lines = [
        "# Auto-generated open",
        # Allow the opener advancement to fire again on the next right-click
        f"advancement revoke @s only {menu['namespace']}:menu/{menu['menu_id']}/opener",
        f"function {menu_function_prefix(menu)}/close",
        "",
        f"summon {container_entity_id(menu['container'])} {summon_coords} {nbt}",
        "",
        "scoreboard players set @s guigen_page 0",
    ]
    for cmd in menu.get("on_open") or []:
        lines.append(str(cmd))
    if menu.get("on_open"):
        lines.append("")
    inited: set[str] = set()
    for w in all_widgets(menu):
        scores_to_init: list[str] = []
        if w.get("toggle"):
            scores_to_init.append(w["toggle"]["score"])
        if w.get("counter_score"):
            scores_to_init.append(w["counter_score"])
        if w.get("progress_score"):
            scores_to_init.append(w["progress_score"])
        if w.get("cycle"):
            scores_to_init.append(w["cycle"]["score"])
        for sc in scores_to_init:
            if sc in inited:
                continue
            inited.add(sc)
            lines.append(
                f"execute unless score @s {sc} matches 0.. run scoreboard players set @s {sc} 0"
            )
    lines.extend(
        [
            f"function {menu_function_prefix(menu)}/fill",
            f"scoreboard players set @s guigen_menu_timer {menu['timer_ticks']}",
            "",
            'tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},'
            '{"text":"Menu opened. Right-click the cart, then SHIFT-click buttons.","color":"yellow"}]',
            "",
        ]
    )
    out[f"{menu_dir_path(menu)}/open.mcfunction"] = "\n".join(lines)


def generate_close(menu: dict[str, Any], out: dict[str, str]) -> None:
    cart = (
        f"@e[type={container_entity_id(menu['container'])},"
        f"tag={menu_tag(menu)},sort=nearest,limit=1]"
    )
    lines = ["# Auto-generated close", "# Empty slots first so kill does not drop GUI items"]
    for slot in range(container_slot_count(menu["container"])):
        lines.append(f"execute as {cart} run {item_air_command('@s', slot)}")
    lines.extend(
        [
            f"kill @e[type={container_entity_id(menu['container'])},tag={menu_tag(menu)}]",
            clear_all_widgets(),
            "clear @s *[custom_data~{guigen:{widget:1}}]",
            "scoreboard players reset @s guigen_menu_timer",
            "scoreboard players reset @s guigen_page",
        ]
    )
    for cmd in menu.get("on_close") or []:
        lines.append(str(cmd))
    lines.append("")
    out[f"{menu_dir_path(menu)}/close.mcfunction"] = "\n".join(lines)


def generate_give_opener(menu: dict[str, Any], out: dict[str, str]) -> None:
    name = (menu.get("opener_name") or "GUI Menu Key").replace("\\", "\\\\").replace('"', '\\"')
    lore = (
        menu.get("opener_lore") or "Right-click to open the menu"
    ).replace("\\", "\\\\").replace('"', '\\"')
    # Knowledge book that "consumes" instantly without particles, then is restored
    # via use_remainder so the key is not destroyed. Advancement opener listens
    # for consume_item and runs the open function.
    components = (
        f'custom_name={{text:"{name}",italic:false,color:"gold"}},'
        f'lore=[{{text:"{lore}",italic:false,color:"gray"}}],'
        "custom_data={guigen:{opener:1b}},"
        'consumable={consume_seconds:0,animation:"none",has_consume_particles:0}'
        "["
    )
    lines = [
        "# Auto-generated give_opener",
        f"give @s minecraft:knowledge_book[{components}] 1",
        "",
        'tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},'
        '{"text":"You received a Menu Key. Right-click to open.","color":"gold"}]',
        "",
    ]
    out[f"{menu_dir_path(menu)}/give_opener.mcfunction"] = "\n".join(lines)

    # Advancement: right-click (consume) the opener book → open menu
    ns = menu["namespace"]
    mid = menu["menu_id"]
    adv_path = f"data/{ns}/advancement/menu/{mid}/opener.json"
    adv = {
        "criteria": {
            "on_right_click": {
                "trigger": "minecraft:consume_item",
                "conditions": {
                    "item": {
                        "items": "minecraft:knowledge_book",
                        "predicates": {
                            "minecraft:custom_data": "{guigen:{opener:1b}}"
                        },
                    }
                },
            }
        },
        "rewards": {
            "function": f"{ns}:menu/{mid}/open"
        },
    }
    out[adv_path] = json.dumps(adv, indent=2) + "\n"


def generate_tags(menu: dict[str, Any], out: dict[str, str]) -> None:
    out["data/minecraft/tags/function/load.json"] = (
        json.dumps({"values": [f"{menu_core_prefix(menu)}/load"]}, indent=2) + "\n"
    )
    out["data/minecraft/tags/function/tick.json"] = (
        json.dumps({"values": [f"{menu_core_prefix(menu)}/tick"]}, indent=2) + "\n"
    )


def generate_pack_mcmeta(out: dict[str, str], description: str) -> None:
    data = {"pack": {"description": description, "min_format": 119, "max_format": 119}}
    out["pack.mcmeta"] = json.dumps(data, indent=2) + "\n"
