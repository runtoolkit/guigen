"""Generate core/load, menu lifecycle, tags, pack.mcmeta."""

from __future__ import annotations
import json
import re
from pathlib import Path

from models.menu import Menu
from builders.paths import menu_dir, core_dir, tags_dir
from builders.snbt import clear_all_widgets, item_air_command


def _cd_score(action_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", action_id)[:40]
    return f"guigen_cd_{safe}"


def generate_load(menu: Menu, out: Path) -> None:
    lines = ["# Auto-generated core load"]
    scores = list(menu.collect_scores())
    for w in menu.interactive_widgets():
        if int(getattr(w, "cooldown_ticks", 0) or 0) > 0:
            sc = _cd_score(w.resolved_action_id())
            if sc not in scores:
                scores.append(sc)
    for score in scores:
        lines.append(f"scoreboard objectives add {score} dummy")
    cart = f"@e[type={menu.container.entity_id},tag={menu.tag}]"
    lines += [
        "",
        f"execute as {cart} run data modify entity @s Items set value []",
        f"kill {cart}",
        "",
        'tellraw @a [{"text":"[GUI-GENERATOR] ","color":"gray"},'
        f'{{"text":"Loaded. /function {menu.function_prefix}/open","color":"green"}}]',
        "",
    ]
    (core_dir(out, menu) / "load.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def generate_open(menu: Menu, out: Path) -> None:
    nbt = menu.container.summon_nbt(
        [f"{menu.namespace}.menu", menu.tag],
        custom_name=menu.display_name,
    )
    lines = [
        "# Auto-generated open",
        f"function {menu.function_prefix}/close",
        "",
        f"summon {menu.container.entity_id} ~ ~ ~ {nbt}",
        "",
        "scoreboard players set @s guigen_page 0",
    ]
    inited: set[str] = set()
    for w in menu.all_widgets():
        scores_to_init = []
        if w.toggle:
            scores_to_init.append(w.toggle.score)
        if w.counter_score:
            scores_to_init.append(w.counter_score)
        if w.progress_score:
            scores_to_init.append(w.progress_score)
        for sc in scores_to_init:
            if sc in inited:
                continue
            inited.add(sc)
            lines.append(
                f"execute unless score @s {sc} matches 0.. "
                f"run scoreboard players set @s {sc} 0"
            )
    lines += [
        f"function {menu.function_prefix}/fill",
        f"scoreboard players set @s guigen_menu_timer {menu.timer_ticks}",
        "",
        'tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},'
        '{"text":"Menu opened. Right-click the cart, then SHIFT-click buttons.","color":"yellow"}]',
        "",
    ]
    (menu_dir(out, menu) / "open.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def generate_close(menu: Menu, out: Path) -> None:
    cart = f"@e[type={menu.container.entity_id},tag={menu.tag},sort=nearest,limit=1]"
    lines = [
        "# Auto-generated close",
        "# Empty slots first so kill does not drop GUI items",
    ]
    for slot in range(menu.container.slot_count):
        lines.append(f"execute as {cart} run {item_air_command('@s', slot)}")
    lines += [
        f"kill @e[type={menu.container.entity_id},tag={menu.tag}]",
        clear_all_widgets(),
        "clear @s *[custom_data~{guigen:{widget:1}}]",
        "scoreboard players reset @s guigen_menu_timer",
        "scoreboard players reset @s guigen_page",
        "",
    ]
    (menu_dir(out, menu) / "close.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def generate_give_opener(menu: Menu, out: Path) -> None:
    name = (menu.opener_name or "GUI Menu Key").replace("\\", "\\\\").replace('"', '\\"')
    lore = (
        menu.opener_lore or f"Run /function {menu.function_prefix}/open"
    ).replace("\\", "\\\\").replace('"', '\\"')
    lines = [
        "# Auto-generated give_opener",
        "give @s minecraft:knowledge_book["
        f'custom_name={{text:"{name}",italic:false,color:"gold"}},'
        f'lore=[{{text:"{lore}",italic:false,color:"gray"}}],'
        "custom_data={guigen:{opener:1b}}] 1",
        "",
        'tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"You received a Menu Key.","color":"gold"}]',
        "",
    ]
    (menu_dir(out, menu) / "give_opener.mcfunction").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def generate_tags(menu: Menu, out: Path) -> None:
    (tags_dir(out) / "load.json").write_text(
        json.dumps({"values": [f"{menu.core_prefix}/load"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    (tags_dir(out) / "tick.json").write_text(
        json.dumps({"values": [f"{menu.core_prefix}/tick"]}, indent=2) + "\n",
        encoding="utf-8",
    )


def generate_pack_mcmeta(out: Path, description: str) -> None:
    data = {
        "pack": {
            "description": description,
            "min_format": 119,
            "max_format": 119,
        }
    }
    (out / "pack.mcmeta").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
