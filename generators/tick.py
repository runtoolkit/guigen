"""Generate tick.mcfunction."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu
from models.widgets import Widget
from builders.snbt import clear_detect_command
from builders.paths import ns_functions


def _detect_block(menu: Menu, item: str, action: str, handler_fn: str) -> list[str]:
    return [
        f"execute as @a[scores={{guigen_menu_timer=1..}}] store success score @s guigen_click "
        f"run {clear_detect_command(item, action)}",
        f"execute as @a[scores={{guigen_click=1}}] at @s run function {handler_fn}",
        "scoreboard players reset @a[scores={guigen_click=1}] guigen_click",
        "",
    ]


def _items_for(w: Widget) -> list[str]:
    if w.toggle is not None:
        return [w.toggle.off_item, w.toggle.on_item]
    return [w.item]


def generate_tick(menu: Menu, out: Path) -> None:
    dist = int(menu.distance_close)
    entity = menu.container.entity_id
    lines: list[str] = [
        "# Auto-generated tick",
        "# Timer",
        "execute as @a[scores={guigen_menu_timer=1..}] run scoreboard players remove @s guigen_menu_timer 1",
        f"execute as @a[scores={{guigen_menu_timer=0}}] at @s run function {menu.function_prefix}/close",
        "",
    ]

    if menu.follow:
        cart = f"@e[type={entity},tag={menu.tag},distance=..{dist},sort=nearest,limit=1]"
        lines += [
            "# Follow + distance safety",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s as {cart} run tp @s ~ ~ ~",
            f"execute as @a[scores={{guigen_menu_timer=1..}}] at @s unless entity "
            f"@e[type={entity},tag={menu.tag},distance=..{dist},limit=1] "
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
        handler = f"{menu.function_prefix}/on_click_{aid}"
        for item in _items_for(w):
            lines.extend(_detect_block(menu, item, aid, handler))

    lines += [
        'kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{guigen:{}}}}}]',
        "",
    ]

    (ns_functions(out, menu) / "tick.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )
