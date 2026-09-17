"""Core tick generator."""

from __future__ import annotations

from typing import Any

from ..components import clear_all_widgets, clear_by_type, clear_by_type_id
from ..models import (
    all_widgets,
    container_entity_id,
    interactive_widgets,
    menu_click_prefix,
    menu_function_prefix,
    menu_tag,
    resolved_action_id,
)
from ..paths import core_dir_path
from .handlers import cd_score

VACUUM_TYPES = ["label", "separator", "progress"]


def detect_block(widget_type: str, widget_id: str, handler_fn: str) -> list[str]:
    return [
        f"execute as @a[scores={{guigen_menu_timer=1..}}] store success score @s guigen_click "
        f"run {clear_by_type_id(widget_type, widget_id, 1)}",
        f"execute as @a[scores={{guigen_click=1}}] at @s run function {handler_fn}",
        "scoreboard players reset @a[scores={guigen_click=1}] guigen_click",
        "",
    ]


def generate_tick(menu: dict[str, Any], out: dict[str, str]) -> None:
    entity = container_entity_id(menu["container"])
    cart = f"@e[type={entity},tag={menu_tag(menu)},sort=nearest,limit=1]"

    lines = [
        "# Auto-generated core tick",
        "# Timer",
        "execute as @a[scores={guigen_menu_timer=1..}] run scoreboard players remove @s guigen_menu_timer 1",
        f"execute as @a[scores={{guigen_menu_timer=0}}] at @s run function {menu_function_prefix(menu)}/close",
        "",
        "# Cooldown tick-down",
    ]

    cd_scores: list[str] = []
    for w in interactive_widgets(menu):
        ticks = int(w.get("cooldown_ticks") or 0)
        if ticks > 0:
            sc = cd_score(resolved_action_id(w))
            if sc not in cd_scores:
                cd_scores.append(sc)
    for sc in cd_scores:
        lines.append(f"execute as @a[scores={{{sc}=1..}}] run scoreboard players remove @s {sc} 1")
    if cd_scores:
        lines.append("")

    if menu.get("follow", True):
        lines.extend(
            [
                "# Follow (cart is kept on the player; distance_close cannot be exceeded)",
                f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s as {cart} run tp @s ~ ~ ~",
                f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s "
                f"unless entity @e[type={entity},tag={menu_tag(menu)},limit=1] "
                f"run function {menu_function_prefix(menu)}/close",
                "",
            ]
        )
    else:
        dist = menu.get("distance_close", 32)
        lines.extend(
            [
                "# Not following — enforce distance_close and cart-presence",
                f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s "
                f"unless entity @e[type={entity},tag={menu_tag(menu)},limit=1] "
                f"run function {menu_function_prefix(menu)}/close",
                f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s "
                f"unless entity @e[type={entity},tag={menu_tag(menu)},distance=..{dist},limit=1] "
                f"run function {menu_function_prefix(menu)}/close",
                "",
            ]
        )

    for w in all_widgets(menu):
        if w.get("toggle") and w["toggle"].get("tick_while_on"):
            for cmd in w["toggle"]["tick_while_on"]:
                lines.append(f"execute as @a[scores={{{w['toggle']['score']}=1}}] run {cmd}")
            lines.append("")

    lines.extend(["# Click detection", ""])

    seen: set[str] = set()
    for w in interactive_widgets(menu):
        aid = resolved_action_id(w)
        if aid in seen:
            continue
        seen.add(aid)
        handler = f"{menu_click_prefix(menu)}/{aid}"
        lines.extend(detect_block(w["kind"], aid, handler))

    lines.extend(["# Vacuum GUI items from player", ""])
    present_kinds = {w["kind"] for w in all_widgets(menu)}
    present_kinds.add("separator")
    for kind in VACUUM_TYPES:
        if kind in present_kinds:
            lines.append(
                f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_by_type(kind)}"
            )
    lines.append(f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_all_widgets()}")
    lines.append(
        "execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{widget:1}}]"
    )

    lines.extend(
        [
            "",
            "# Restore layout every tick",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s "
            f"run function {menu_function_prefix(menu)}/fill",
            "",
            "# Kill dropped GUI items",
            'kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{guigen:{widget:1}}}}}]',
            "kill @e[type=minecraft:item,nbt={Item:{components:{custom_data:{guigen:{widget:1}}}}}]",
            "",
        ]
    )

    out[f"{core_dir_path(menu)}/tick.mcfunction"] = "\n".join(lines)
