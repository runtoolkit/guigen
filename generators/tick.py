"""Generate tick.mcfunction."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu
from builders.snbt import clear_by_type_id, clear_by_type, clear_all_widgets
from builders.paths import ns_functions

_VACUUM_TYPES = ("label", "separator", "progress")


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
    # Global tag selector — never filter by distance so walking does not break fill/follow.
    cart = f"@e[type={entity},tag={menu.tag},sort=nearest,limit=1]"

    lines: list[str] = [
        "# Auto-generated tick",
        "# Timer",
        "execute as @a[scores={guigen_menu_timer=1..}] run scoreboard players remove @s guigen_menu_timer 1",
        f"execute as @a[scores={{guigen_menu_timer=0}}] at @s run function {menu.function_prefix}/close",
        "",
    ]

    if menu.follow:
        lines += [
            "# Follow: always tp tagged cart onto the player (no distance filter)",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s as {cart} run tp @s ~ ~ ~",
            # Only close if the cart entity is completely gone (killed), not if far away.
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

    lines += [
        "# Click detection – clear by custom_data type+id (any item id)",
        "",
    ]

    seen: set[str] = set()
    for w in menu.interactive_widgets():
        aid = w.resolved_action_id()
        if aid in seen:
            continue
        seen.add(aid)
        handler = f"{menu.function_prefix}/on_click_{aid}"
        lines.extend(_detect_block(w.kind, aid, handler))

    lines += [
        "# Vacuum every GUI widget from the player (display + leftovers + cursor)",
        "",
    ]
    present_kinds = {w.kind for w in menu.all_widgets()}
    present_kinds.add("separator")
    for kind in _VACUUM_TYPES:
        if kind in present_kinds:
            lines.append(
                f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_by_type(kind)}"
            )
    # Catch-all: anything still carrying widget:1
    lines.append(
        f"execute as @a[scores={{guigen_menu_timer=1..}}] run {clear_all_widgets()}"
    )
    # Also clear by bare custom_data path (some builds prefer non-namespaced component key)
    lines.append(
        'execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{widget:1}}]'
    )

    lines += [
        "",
        "# Restore full layout every tick",
        f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s run function {menu.function_prefix}/fill",
        "",
        "# Kill dropped GUI items",
        'kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{guigen:{widget:1}}}}}]',
        'kill @e[type=minecraft:item,nbt={Item:{components:{custom_data:{guigen:{widget:1}}}}}]',
        "",
    ]

    (ns_functions(out, menu) / "tick.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )
