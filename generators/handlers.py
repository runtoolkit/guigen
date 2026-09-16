"""Generate on_click_*.mcfunction handlers for interactive widgets."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu
from models.widgets import Widget
from models.components import Text
from builders.paths import menu_dir


def _escape_json(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _tellraw_line(msg: Text) -> str:
    parts = [f'"text":"{_escape_json(msg.text)}"', '"italic":false']
    if msg.color:
        parts.append(f'"color":"{msg.color}"')
    body = "{" + ",".join(parts) + "}"
    return f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},{body}]'


def _handler_for(menu: Menu, w: Widget) -> list[str]:
    aid = w.resolved_action_id()
    lines: list[str] = [f"# Handler: {aid} ({w.kind})", ""]

    if w.kind == "close":
        msg = w.success_message or Text("Menu closed.", color="red")
        lines.append(_tellraw_line(msg))
        lines.append(f"function {menu.function_prefix}/close")
        return lines

    if w.kind == "nav":
        assert w.target_page is not None
        lines.append(f"scoreboard players set @s guigen_page {w.target_page}")
        lines.append(f"function {menu.function_prefix}/fill")
        if w.success_message:
            lines.append(_tellraw_line(w.success_message))
        return lines

    if w.kind == "confirm":
        assert w.confirm_page is not None
        lines.append(f"scoreboard players set @s guigen_page {w.confirm_page}")
        lines.append(f"function {menu.function_prefix}/fill")
        msg = w.success_message or Text("Confirm?", color="gold")
        lines.append(_tellraw_line(msg))
        return lines

    if w.kind == "toggle":
        assert w.toggle is not None
        t = w.toggle
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
        # `scoreboard players add` only accepts non-negative literals in
        # vanilla syntax; a negative delta must go through `remove` with
        # its absolute value instead, or the command is invalid.
        step_cmd = (
            f"scoreboard players add @s {s} {d}"
            if d >= 0
            else f"scoreboard players remove @s {s} {abs(d)}"
        )
        lines += [
            step_cmd,
            # clamp
            f"execute if score @s {s} matches {mx + 1}.. run scoreboard players set @s {s} {mx}",
            f"execute if score @s {s} matches ..{mn - 1} run scoreboard players set @s {s} {mn}",
            f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},'
            f'{{"text":"{s} = ","color":"yellow"}},'
            f'{{"score":{{"name":"@s","objective":"{s}"}},"color":"gold"}}]',
            f"function {menu.function_prefix}/fill",
        ]
        return lines

    # button with optional condition
    if w.condition is not None:
        cond = w.condition
        fail = cond.fail_message or Text("Condition failed.", color="red")

        if cond.type == "item_count_lt":
            assert cond.item and cond.max_count is not None
            lines.append(
                f"execute store result score @s guigen_tmp run clear @s {cond.item} 0"
            )
            lines.append(
                f"execute if score @s guigen_tmp matches {cond.max_count}.. run {_tellraw_line(fail)}"
            )
            for c in w.commands:
                lines.append(
                    f"execute if score @s guigen_tmp matches ..{cond.max_count - 1} run {c}"
                )
            if w.success_message:
                lines.append(
                    f"execute if score @s guigen_tmp matches ..{cond.max_count - 1} run "
                    + _tellraw_line(w.success_message)
                )

        elif cond.type == "item_count_gte":
            assert cond.item and cond.min_count is not None
            lines.append(
                f"execute store result score @s guigen_tmp run clear @s {cond.item} 0"
            )
            lines.append(
                f"execute if score @s guigen_tmp matches ..{cond.min_count - 1} run {_tellraw_line(fail)}"
            )
            for c in w.commands:
                lines.append(
                    f"execute if score @s guigen_tmp matches {cond.min_count}.. run {c}"
                )
            if w.success_message:
                lines.append(
                    f"execute if score @s guigen_tmp matches {cond.min_count}.. run "
                    + _tellraw_line(w.success_message)
                )

        elif cond.type == "score":
            assert cond.score and cond.matches is not None
            for c in w.commands:
                lines.append(
                    f"execute if score @s {cond.score} matches {cond.matches} run {c}"
                )
            lines.append(
                f"execute unless score @s {cond.score} matches {cond.matches} run {_tellraw_line(fail)}"
            )
            if w.success_message:
                lines.append(
                    f"execute if score @s {cond.score} matches {cond.matches} run "
                    + _tellraw_line(w.success_message)
                )

        elif cond.type == "has_tag":
            assert cond.tag is not None
            for c in w.commands:
                lines.append(f"execute if entity @s[tag={cond.tag}] run {c}")
            lines.append(
                f"execute unless entity @s[tag={cond.tag}] run {_tellraw_line(fail)}"
            )
            if w.success_message:
                lines.append(
                    f"execute if entity @s[tag={cond.tag}] run {_tellraw_line(w.success_message)}"
                )

        elif cond.type == "gamemode":
            assert cond.gamemode is not None
            for c in w.commands:
                lines.append(f"execute if entity @s[gamemode={cond.gamemode}] run {c}")
            lines.append(
                f"execute unless entity @s[gamemode={cond.gamemode}] run {_tellraw_line(fail)}"
            )
            if w.success_message:
                lines.append(
                    f"execute if entity @s[gamemode={cond.gamemode}] run {_tellraw_line(w.success_message)}"
                )

        else:
            # unknown condition type – still run commands (no guard)
            for c in w.commands:
                lines.append(c)
            if w.success_message:
                lines.append(_tellraw_line(w.success_message))

        lines.append(f"function {menu.function_prefix}/fill")
        return lines

    # plain button / run_commands
    for c in w.commands:
        lines.append(c)
    if w.success_message:
        lines.append(_tellraw_line(w.success_message))
    lines.append(f"function {menu.function_prefix}/fill")
    return lines


def generate_handlers(menu: Menu, out: Path) -> None:
    seen: set[str] = set()
    for w in menu.interactive_widgets():
        aid = w.resolved_action_id()
        if aid in seen:
            continue
        seen.add(aid)
        content = "\n".join(_handler_for(menu, w)).rstrip() + "\n"
        path = menu_dir(out, menu) / f"on_click_{aid}.mcfunction"
        path.write_text(content, encoding="utf-8")