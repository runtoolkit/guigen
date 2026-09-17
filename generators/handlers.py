"""Generate menu/<id>/click/<action>.mcfunction handlers."""

from __future__ import annotations
from pathlib import Path
import re

from models.menu import Menu
from models.widgets import Widget, Cost
from models.components import Text
from builders.paths import click_dir


def _escape_json(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _tellraw_line(msg: Text) -> str:
    parts = [f'"text":"{_escape_json(msg.text)}"', '"italic":false']
    if msg.color:
        parts.append(f'"color":"{msg.color}"')
    body = "{" + ",".join(parts) + "}"
    return f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},{body}]'


def _playsound(sound: str | None) -> list[str]:
    if not sound:
        return []
    return [f"playsound {sound} master @s ~ ~ ~ 1 1"]


def _cd_score(action_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", action_id)[:40]
    return f"guigen_cd_{safe}"


def _cooldown_guard(w: Widget) -> list[str]:
    ticks = int(getattr(w, "cooldown_ticks", 0) or 0)
    if ticks <= 0:
        return []
    sc = _cd_score(w.resolved_action_id())
    msg = Text("Please wait…", color="red")
    return [
        f"# cooldown {ticks}t -> {sc}",
        f"execute if score @s {sc} matches 1.. run {_tellraw_line(msg)}",
        f"execute if score @s {sc} matches 1.. run return 1",
        f"scoreboard players set @s {sc} {ticks}",
        "",
    ]


def _cost_guard(w: Widget) -> list[str]:
    cost: Cost | None = getattr(w, "cost", None)
    if cost is None:
        return []
    fail = cost.fail_message or Text("Not enough resources.", color="red")
    lines = ["# cost check"]
    if cost.item:
        lines.append(
            f"execute store result score @s guigen_tmp run clear @s {cost.item} 0"
        )
        lines.append(
            f"execute if score @s guigen_tmp matches ..{cost.count - 1} run {_tellraw_line(fail)}"
        )
        lines.append(
            f"execute if score @s guigen_tmp matches ..{cost.count - 1} run return 1"
        )
        lines.append(f"clear @s {cost.item} {cost.count}")
    if cost.score:
        lines.append(
            f"execute unless score @s {cost.score} matches {cost.amount}.. run {_tellraw_line(fail)}"
        )
        lines.append(
            f"execute unless score @s {cost.score} matches {cost.amount}.. run return 1"
        )
        lines.append(f"scoreboard players remove @s {cost.score} {cost.amount}")
    lines.append("")
    return lines


def _emit_actions(w: Widget, prefix: str = "") -> list[str]:
    lines: list[str] = []
    for c in w.commands:
        lines.append(f"{prefix}{c}" if prefix else c)
    for fn in getattr(w, "functions", None) or []:
        cmd = f"function {fn}"
        lines.append(f"{prefix}{cmd}" if prefix else cmd)
    for s in _playsound(getattr(w, "sound", None)):
        lines.append(f"{prefix}{s}" if prefix else s)
    return lines


def _handler_for(menu: Menu, w: Widget) -> list[str]:
    aid = w.resolved_action_id()
    lines: list[str] = [f"# Handler: {aid} ({w.kind})", ""]

    if w.kind != "close":
        lines.extend(_cooldown_guard(w))
        if getattr(w, "cost", None) is not None:
            lines.extend(_cost_guard(w))

    if w.kind == "close":
        lines.extend(_playsound(w.sound))
        msg = w.success_message or Text("Menu closed.", color="red")
        lines.append(_tellraw_line(msg))
        lines.append(f"function {menu.function_prefix}/close")
        return lines

    if w.kind == "nav":
        assert w.target_page is not None
        lines.extend(_playsound(w.sound))
        lines.append(f"scoreboard players set @s guigen_page {w.target_page}")
        lines.append(f"function {menu.function_prefix}/fill")
        if w.success_message:
            lines.append(_tellraw_line(w.success_message))
        return lines

    if w.kind == "confirm":
        assert w.confirm_page is not None
        lines.extend(_playsound(w.sound))
        lines.append(f"scoreboard players set @s guigen_page {w.confirm_page}")
        lines.append(f"function {menu.function_prefix}/fill")
        msg = w.success_message or Text("Confirm?", color="gold")
        lines.append(_tellraw_line(msg))
        return lines

    if w.kind == "toggle":
        assert w.toggle is not None
        t = w.toggle
        lines.extend(_playsound(w.sound))
        lines += [
            f"execute if score @s {t.score} matches 1 run scoreboard players set @s guigen_tmp 1",
            f"execute if score @s {t.score} matches 0 run scoreboard players set @s {t.score} 1",
            f"execute if score @s guigen_tmp matches 1 run scoreboard players set @s {t.score} 0",
            "scoreboard players reset @s guigen_tmp",
            "",
        ]
        for c in t.on_commands:
            lines.append(f"execute if score @s {t.score} matches 1 run {c}")
        for c in t.off_commands:
            lines.append(f"execute if score @s {t.score} matches 0 run {c}")
        lines.append("")
        lines.append(f"execute if score @s {t.score} matches 1 run {_tellraw_line(t.on_name)}")
        lines.append(f"execute if score @s {t.score} matches 0 run {_tellraw_line(t.off_name)}")
        lines.append(f"function {menu.function_prefix}/fill")
        return lines

    if w.kind == "counter":
        assert w.counter_score is not None
        s = w.counter_score
        d = w.counter_delta
        mn, mx = w.counter_min, w.counter_max
        step_cmd = (
            f"scoreboard players add @s {s} {d}"
            if d >= 0
            else f"scoreboard players remove @s {s} {abs(d)}"
        )
        lines.extend(_playsound(w.sound))
        lines += [
            step_cmd,
            f"execute if score @s {s} matches {mx + 1}.. run scoreboard players set @s {s} {mx}",
            f"execute if score @s {s} matches ..{mn - 1} run scoreboard players set @s {s} {mn}",
            f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},'
            f'{{"text":"{s} = ","color":"yellow"}},'
            f'{{"score":{{"name":"@s","objective":"{s}"}},"color":"gold"}}]',
            f"function {menu.function_prefix}/fill",
        ]
        return lines

    if w.condition is not None:
        cond = w.condition
        fail = cond.fail_message or Text("Condition failed.", color="red")

        def _success_block(prefix: str) -> list[str]:
            block: list[str] = []
            block.extend(_emit_actions(w, prefix=prefix))
            if w.success_message:
                block.append(f"{prefix}{_tellraw_line(w.success_message)}")
            return block

        if cond.type == "item_count_lt":
            assert cond.item and cond.max_count is not None
            lines.append(
                f"execute store result score @s guigen_tmp run clear @s {cond.item} 0"
            )
            lines.append(
                f"execute if score @s guigen_tmp matches {cond.max_count}.. run {_tellraw_line(fail)}"
            )
            ok = f"execute if score @s guigen_tmp matches ..{cond.max_count - 1} run "
            lines.extend(_success_block(ok))
        elif cond.type == "item_count_gte":
            assert cond.item and cond.min_count is not None
            lines.append(
                f"execute store result score @s guigen_tmp run clear @s {cond.item} 0"
            )
            lines.append(
                f"execute if score @s guigen_tmp matches ..{cond.min_count - 1} run {_tellraw_line(fail)}"
            )
            ok = f"execute if score @s guigen_tmp matches {cond.min_count}.. run "
            lines.extend(_success_block(ok))
        elif cond.type == "score":
            assert cond.score and cond.matches is not None
            ok = f"execute if score @s {cond.score} matches {cond.matches} run "
            lines.extend(_success_block(ok))
            lines.append(
                f"execute unless score @s {cond.score} matches {cond.matches} run {_tellraw_line(fail)}"
            )
        elif cond.type == "has_tag":
            assert cond.tag is not None
            ok = f"execute if entity @s[tag={cond.tag}] run "
            lines.extend(_success_block(ok))
            lines.append(
                f"execute unless entity @s[tag={cond.tag}] run {_tellraw_line(fail)}"
            )
        elif cond.type == "gamemode":
            assert cond.gamemode is not None
            ok = f"execute if entity @s[gamemode={cond.gamemode}] run "
            lines.extend(_success_block(ok))
            lines.append(
                f"execute unless entity @s[gamemode={cond.gamemode}] run {_tellraw_line(fail)}"
            )
        else:
            lines.extend(_emit_actions(w))
            if w.success_message:
                lines.append(_tellraw_line(w.success_message))

        lines.append(f"function {menu.function_prefix}/fill")
        return lines

    lines.extend(_emit_actions(w))
    if w.success_message:
        lines.append(_tellraw_line(w.success_message))
    lines.append(f"function {menu.function_prefix}/fill")
    return lines


def generate_handlers(menu: Menu, out: Path) -> None:
    seen: set[str] = set()
    cdir = click_dir(out, menu)
    for w in menu.interactive_widgets():
        aid = w.resolved_action_id()
        if aid in seen:
            continue
        seen.add(aid)
        content = "\n".join(_handler_for(menu, w)).rstrip() + "\n"
        (cdir / f"{aid}.mcfunction").write_text(content, encoding="utf-8")
