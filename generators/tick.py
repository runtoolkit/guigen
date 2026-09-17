"""Generate core/tick.mcfunction."""

from __future__ import annotations
from pathlib import Path
import re

from models.menu import Menu
from builders.snbt import clear_by_type_id, clear_by_type, clear_all_widgets
from builders.paths import core_dir

_VACUUM_TYPES = ("label", "separator", "progress")


def _cd_score(action_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", action_id)[:40]
    return f"guigen_cd_{safe}"


def _detect_block(widget_type: str, widget_id: str, handler_fn: str) -> list[str]:
    return [
        f"execute as @a[scores={{guigen_menu_timer=1..}}] store success score @s guigen_click "
        f"run {clear_by_type_id(widget_type, widget_id, 1)}",
        f"execute as @a[scores={{guigen_click=1}}] at @s run function {handler_fn}",
        "scoreboard players reset @a[scores={guigen_click=1}] guigen_click",
        "",
    ]


def generate_tick(menu: Menu, out: Path) -> None:
    entity = menu.container.entity_id
    cart = f"@e[type={entity},tag={menu.tag},sort=nearest,limit=1]"

    lines: list[str] = [
        "# Auto-generated core tick",
        "# Timer",
        "execute as @a[scores={guigen_menu_timer=1..}] run scoreboard players remove @s guigen_menu_timer 1",
        f"execute as @a[scores={{guigen_menu_timer=0}}] at @s run function {menu.function_prefix}/close",
        "",
        "# Cooldown tick-down",
    ]

    cd_scores: list[str] = []
    for w in menu.interactive_widgets():
        ticks = int(getattr(w, "cooldown_ticks", 0) or 0)
        if ticks > 0:
            sc = _cd_score(w.resolved_action_id())
            if sc not in cd_scores:
                cd_scores.append(sc)
    for sc in cd_scores:
        lines.append(
            f"execute as @a[scores={{{sc}=1..}}] run scoreboard players remove @s {sc} 1"
        )
    if cd_scores:
        lines.append("")

    if menu.follow:
        lines += [
            "# Follow (no distance filter)",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s as {cart} run tp @s ~ ~ ~",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s unless entity "
            f"@e[type={entity},tag={menu.tag},limit=1] "
            f"run function {menu.function_prefix}/close",
            "",
        ]

    for w in menu.all_widgets():
        if w.toggle and w.toggle.tick_while_on:
            for cmd in w.toggle.tick_while_on:
                lines.append(f"execute as @a[scores={{{w.toggle.score}=1}}] run {cmd}")
            lines.append("")

    lines += ["# Click detection", ""]

    seen: set[str] = set()
    for w in menu.interactive_widgets():
        aid = w.resolved_action_id()
        if aid in seen:
            continue
        seen.add(aid)
        handler = f"{menu.click_prefix}/{aid}"
        lines.extend(_detect_block(w.kind, aid, handler))

    lines += ["# Vacuum GUI items from player", ""]
    present_kinds = {w.kind for w in menu.all_widgets()}
    present_kinds.add("separator")
    for kind in _VACUUM_TYPES:
        if kind in present_kinds:
            lines.append(
                f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_by_type(kind)}"
            )
    lines.append(
        f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_all_widgets()}"
    )
    lines.append(
        'execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{widget:1}}]'
    )

    lines += [
        "",
        "# Restore layout every tick",
        f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s run function {menu.function_prefix}/fill",
        "",
        "# Kill dropped GUI items",
        'kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{guigen:{widget:1}}}}}]',
        'kill @e[type=minecraft:item,nbt={Item:{components:{custom_data:{guigen:{widget:1}}}}}]',
        "",
    ]

    (core_dir(out, menu) / "tick.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )
