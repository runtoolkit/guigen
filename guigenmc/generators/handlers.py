"""Click handler generators."""

from __future__ import annotations

from typing import Any

from ..components import clear_by_type_id  # noqa: F401 — kept for parity
from ..models import interactive_widgets, menu_function_prefix, resolved_action_id
from ..paths import click_dir_path


def escape_json(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def tellraw_line(msg: dict[str, Any]) -> str:
    parts = [f'"text":"{escape_json(msg["text"])}"', '"italic":false']
    if msg.get("color"):
        parts.append(f'"color":"{msg["color"]}"')
    body = "{" + ",".join(parts) + "}"
    return f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},{body}]'


def playsound(sound: str | None) -> list[str]:
    if not sound:
        return []
    return [f"playsound {sound} master @s ~ ~ ~ 1 1"]


def cd_score(action_id: str) -> str:
    safe = "".join(c if c.isalnum() or c == "_" else "_" for c in str(action_id))[:40]
    return f"guigen_cd_{safe}"


def cooldown_guard(w: dict[str, Any]) -> list[str]:
    ticks = int(w.get("cooldown_ticks") or 0)
    if ticks <= 0:
        return []
    sc = cd_score(resolved_action_id(w))
    msg = {"text": "Please wait…", "italic": False, "color": "red", "bold": None, "underlined": None}
    return [
        f"# cooldown {ticks}t -> {sc}",
        f"execute if score @s {sc} matches 1.. run {tellraw_line(msg)}",
        f"execute if score @s {sc} matches 1.. run return 1",
        f"scoreboard players set @s {sc} {ticks}",
        "",
    ]


def cost_guard(w: dict[str, Any]) -> list[str]:
    cost = w.get("cost")
    if cost is None:
        return []
    fail = cost.get("fail_message") or {
        "text": "Not enough resources.",
        "italic": False,
        "color": "red",
        "bold": None,
        "underlined": None,
    }
    lines = ["# cost check"]
    if cost.get("item"):
        lines.append(f"execute store result score @s guigen_tmp run clear @s {cost['item']} 0")
        lines.append(
            f"execute if score @s guigen_tmp matches ..{cost['count'] - 1} run {tellraw_line(fail)}"
        )
        lines.append(f"execute if score @s guigen_tmp matches ..{cost['count'] - 1} run return 1")
        lines.append(f"clear @s {cost['item']} {cost['count']}")
    if cost.get("score"):
        lines.append(
            f"execute unless score @s {cost['score']} matches {cost['amount']}.. "
            f"run {tellraw_line(fail)}"
        )
        lines.append(
            f"execute unless score @s {cost['score']} matches {cost['amount']}.. run return 1"
        )
        lines.append(f"scoreboard players remove @s {cost['score']} {cost['amount']}")
    lines.append("")
    return lines


def emit_actions(w: dict[str, Any], prefix: str = "") -> list[str]:
    lines: list[str] = []
    for c in w.get("commands") or []:
        lines.append(f"{prefix}{c}" if prefix else c)
    for fn in w.get("functions") or []:
        cmd = f"function {fn}"
        lines.append(f"{prefix}{cmd}" if prefix else cmd)
    for s in playsound(w.get("sound")):
        lines.append(f"{prefix}{s}" if prefix else s)
    return lines


def handler_for(menu: dict[str, Any], w: dict[str, Any]) -> list[str]:
    aid = resolved_action_id(w)
    lines: list[str] = [f"# Handler: {aid} ({w['kind']})", ""]

    if w["kind"] != "close":
        lines.append("# Interaction keeps the menu open — reset auto-close timer")
        lines.append(f"scoreboard players set @s guigen_menu_timer {menu['timer_ticks']}")
        lines.append("")
        lines.extend(cooldown_guard(w))
        if w.get("cost") is not None:
            lines.extend(cost_guard(w))

    if w["kind"] == "close":
        lines.extend(playsound(w.get("sound")))
        msg = w.get("success_message") or {
            "text": "Menu closed.",
            "italic": False,
            "color": "red",
            "bold": None,
            "underlined": None,
        }
        lines.append(tellraw_line(msg))
        lines.append(f"function {menu_function_prefix(menu)}/close")
        return lines

    if w["kind"] == "nav":
        lines.extend(playsound(w.get("sound")))
        lines.append(f"scoreboard players set @s guigen_page {w['target_page']}")
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        if w.get("success_message"):
            lines.append(tellraw_line(w["success_message"]))
        return lines

    if w["kind"] == "confirm":
        lines.extend(playsound(w.get("sound")))
        lines.append(f"scoreboard players set @s guigen_page {w['confirm_page']}")
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        msg = w.get("success_message") or {
            "text": "Confirm?",
            "italic": False,
            "color": "gold",
            "bold": None,
            "underlined": None,
        }
        lines.append(tellraw_line(msg))
        return lines

    if w["kind"] == "toggle":
        t = w["toggle"]
        lines.extend(playsound(w.get("sound")))
        lines.extend(
            [
                f"execute if score @s {t['score']} matches 1 run scoreboard players set @s guigen_tmp 1",
                f"execute if score @s {t['score']} matches 0 run scoreboard players set @s {t['score']} 1",
                f"execute if score @s guigen_tmp matches 1 run scoreboard players set @s {t['score']} 0",
                "scoreboard players reset @s guigen_tmp",
                "",
            ]
        )
        for c in t.get("on_commands") or []:
            lines.append(f"execute if score @s {t['score']} matches 1 run {c}")
        for c in t.get("off_commands") or []:
            lines.append(f"execute if score @s {t['score']} matches 0 run {c}")
        lines.append("")
        lines.append(f"execute if score @s {t['score']} matches 1 run {tellraw_line(t['on_name'])}")
        lines.append(f"execute if score @s {t['score']} matches 0 run {tellraw_line(t['off_name'])}")
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        return lines

    if w["kind"] == "random":
        rewards = w["random"]["rewards"]
        total_weight = sum(r["weight"] for r in rewards)
        lines.extend(playsound(w.get("sound")))
        lines.append(
            f"execute store result score @s guigen_rand run random value 0..{total_weight - 1}"
        )
        lines.append("")
        lo = 0
        for r in rewards:
            hi = lo + r["weight"] - 1
            guard = f"execute if score @s guigen_rand matches {lo}..{hi} run "
            for c in r.get("commands") or []:
                lines.append(f"{guard}{c}")
            for fn in r.get("functions") or []:
                lines.append(f"{guard}function {fn}")
            if r.get("message"):
                lines.append(f"{guard}{tellraw_line(r['message'])}")
            lo = hi + 1
        lines.append("")
        lines.append("scoreboard players reset @s guigen_rand")
        if w.get("success_message"):
            lines.append(tellraw_line(w["success_message"]))
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        return lines

    if w["kind"] == "counter":
        s = w["counter_score"]
        d = w["counter_delta"]
        mn, mx = w["counter_min"], w["counter_max"]
        step_cmd = (
            f"scoreboard players add @s {s} {d}"
            if d >= 0
            else f"scoreboard players remove @s {s} {abs(d)}"
        )
        lines.extend(playsound(w.get("sound")))
        lines.append(step_cmd)
        if w.get("counter_wrap"):
            lines.extend(
                [
                    f"execute if score @s {s} matches {mx + 1}.. run scoreboard players set @s {s} {mn}",
                    f"execute if score @s {s} matches ..{mn - 1} run scoreboard players set @s {s} {mx}",
                ]
            )
            if (mx - mn + 1) <= 0:
                lines.append("# warning: counter_min >= counter_max, wrap has no valid range")
        else:
            lines.extend(
                [
                    f"execute if score @s {s} matches {mx + 1}.. run scoreboard players set @s {s} {mx}",
                    f"execute if score @s {s} matches ..{mn - 1} run scoreboard players set @s {s} {mn}",
                ]
            )
        lines.extend(
            [
                f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},'
                f'{{"text":"{s} = ","color":"yellow"}},'
                f'{{"score":{{"name":"@s","objective":"{s}"}},"color":"gold"}}]',
                f"function {menu_function_prefix(menu)}/fill",
            ]
        )
        return lines

    if w["kind"] == "link":
        lines.extend(playsound(w.get("sound")))
        url = w.get("url") or ""
        link_text = w.get("link_text") or {
            "text": "Click here to open",
            "italic": False,
            "color": "aqua",
            "bold": None,
            "underlined": True,
        }
        # Minecraft 1.21.5+: clickEvent → click_event, value → url
        body = (
            f'{{"text":"{escape_json(link_text.get("text") or "Open link")}",'
            f'"italic":false,'
            f'"color":"{link_text.get("color") or "aqua"}",'
            f'"underlined":true,'
            f'"click_event":{{"action":"open_url","url":"{escape_json(url)}"}}'
            f'}}'
        )
        lines.append(
            f'tellraw @s [{{"text":"[GUI-GENERATOR] ","color":"gray"}},{body}]'
        )
        if w.get("success_message"):
            lines.append(tellraw_line(w["success_message"]))
        # Keep menu open
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        return lines

    if w["kind"] == "cycle":
        c = w["cycle"]
        score = c["score"]
        n = len(c["options"])
        lines.extend(playsound(w.get("sound")))
        lines.append(f"scoreboard players add @s {score} 1")
        if c.get("wrap", True):
            lines.append(
                f"execute if score @s {score} matches {n}.. run scoreboard players set @s {score} 0"
            )
        else:
            lines.append(
                f"execute if score @s {score} matches {n}.. run scoreboard players set @s {score} {n - 1}"
            )
        # Run option-specific commands
        for i, opt in enumerate(c["options"]):
            guard = f"execute if score @s {score} matches {i} run "
            for cmd in opt.get("commands") or []:
                lines.append(f"{guard}{cmd}")
            for fn in opt.get("functions") or []:
                lines.append(f"{guard}function {fn}")
        # Feedback with current option name
        for i, opt in enumerate(c["options"]):
            name = opt.get("name") or {"text": f"Option {i}", "color": "yellow"}
            lines.append(
                f"execute if score @s {score} matches {i} run {tellraw_line(name)}"
            )
        lines.append(f"function {menu_function_prefix(menu)}/fill")
        return lines

    if w.get("condition") is not None:
        cond = w["condition"]
        fail = cond.get("fail_message") or {
            "text": "Condition failed.",
            "italic": False,
            "color": "red",
            "bold": None,
            "underlined": None,
        }

        def success_block(prefix: str) -> list[str]:
            block = emit_actions(w, prefix)
            if w.get("success_message"):
                block.append(f"{prefix}{tellraw_line(w['success_message'])}")
            return block

        if cond["type"] == "item_count_lt":
            lines.append(f"execute store result score @s guigen_tmp run clear @s {cond['item']} 0")
            lines.append(
                f"execute if score @s guigen_tmp matches {cond['max_count']}.. run {tellraw_line(fail)}"
            )
            ok = f"execute if score @s guigen_tmp matches ..{cond['max_count'] - 1} run "
            lines.extend(success_block(ok))
        elif cond["type"] == "item_count_gte":
            lines.append(f"execute store result score @s guigen_tmp run clear @s {cond['item']} 0")
            lines.append(
                f"execute if score @s guigen_tmp matches ..{cond['min_count'] - 1} "
                f"run {tellraw_line(fail)}"
            )
            ok = f"execute if score @s guigen_tmp matches {cond['min_count']}.. run "
            lines.extend(success_block(ok))
        elif cond["type"] == "score":
            ok = f"execute if score @s {cond['score']} matches {cond['matches']} run "
            lines.extend(success_block(ok))
            lines.append(
                f"execute unless score @s {cond['score']} matches {cond['matches']} "
                f"run {tellraw_line(fail)}"
            )
        elif cond["type"] == "has_tag":
            ok = f"execute if entity @s[tag={cond['tag']}] run "
            lines.extend(success_block(ok))
            lines.append(f"execute unless entity @s[tag={cond['tag']}] run {tellraw_line(fail)}")
        elif cond["type"] == "gamemode":
            ok = f"execute if entity @s[gamemode={cond['gamemode']}] run "
            lines.extend(success_block(ok))
            lines.append(
                f"execute unless entity @s[gamemode={cond['gamemode']}] run {tellraw_line(fail)}"
            )
        elif cond["type"] == "has_advancement":
            adv = cond.get("advancement") or ""
            ok = f"execute if entity @s[advancements={{{adv}=true}}] run "
            lines.extend(success_block(ok))
            lines.append(
                f"execute unless entity @s[advancements={{{adv}=true}}] run {tellraw_line(fail)}"
            )
        else:
            lines.extend(emit_actions(w))
            if w.get("success_message"):
                lines.append(tellraw_line(w["success_message"]))

        lines.append(f"function {menu_function_prefix(menu)}/fill")
        return lines

    lines.extend(emit_actions(w))
    if w.get("success_message"):
        lines.append(tellraw_line(w["success_message"]))
    lines.append(f"function {menu_function_prefix(menu)}/fill")
    return lines


def generate_handlers(menu: dict[str, Any], out: dict[str, str]) -> None:
    seen: set[str] = set()
    for w in interactive_widgets(menu):
        aid = resolved_action_id(w)
        if aid in seen:
            continue
        seen.add(aid)
        content = "\n".join(handler_for(menu, w)).rstrip() + "\n"
        out[f"{click_dir_path(menu)}/{aid}.mcfunction"] = content
