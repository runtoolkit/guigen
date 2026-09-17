"""Page fill generators."""

from __future__ import annotations

from typing import Any

from ..components import item_replace_command, mk_item_components
from ..models import (
    components_for_toggle,
    container_entity_id,
    container_slot_count,
    gui_custom_data,
    menu_page_prefix,
    menu_tag,
    mk_separator_widget,
    occupied_slots,
    resolved_action_id,
    widget_components,
)
from ..paths import menu_dir_path, page_dir_path


def cart_selector(menu: dict[str, Any]) -> str:
    return (
        f"@e[type={container_entity_id(menu['container'])},"
        f"tag={menu_tag(menu)},sort=nearest,limit=1]"
    )


def generate_fill_router(menu: dict[str, Any], out: dict[str, str]) -> None:
    lines = ["# Auto-generated – route to current page (every slot is overwritten)", ""]
    for page in menu["pages"]:
        lines.append(
            f"execute if score @s guigen_page matches {page['index']} "
            f"run function {menu_page_prefix(menu)}/{page['index']}"
        )
    out[f"{menu_dir_path(menu)}/fill.mcfunction"] = "\n".join(lines) + "\n"


def emit_static(menu: dict[str, Any], w: dict[str, Any]) -> list[str]:
    return [item_replace_command(cart_selector(menu), w["slot"], w["item"], widget_components(w))]


def emit_toggle(menu: dict[str, Any], w: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for state in (0, 1):
        item, comps = components_for_toggle(w, state)
        cmd = item_replace_command(cart_selector(menu), w["slot"], item, comps)
        lines.append(f"execute if score @s {w['toggle']['score']} matches {state} run {cmd}")
    return lines


def emit_progress(menu: dict[str, Any], w: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    width = w["progress_width"]
    mx = w["progress_max"]
    for i in range(width):
        slot = w["slot"] + i
        threshold = (i * mx) // width
        empty_comps = mk_item_components(
            custom_name=w.get("name") or {"text": " ", "italic": False, "color": None, "bold": None, "underlined": None},
            custom_data=gui_custom_data(w, slot),
        )
        full_comps = mk_item_components(
            custom_name=w.get("name") or {"text": " ", "italic": False, "color": None, "bold": None, "underlined": None},
            custom_data=gui_custom_data(w, slot),
        )
        empty_cmd = item_replace_command(cart_selector(menu), slot, w["progress_empty_item"], empty_comps)
        full_cmd = item_replace_command(cart_selector(menu), slot, w["progress_full_item"], full_comps)
        lines.append(empty_cmd)
        if i == 0:
            lines.append(f"execute if score @s {w['progress_score']} matches 1.. run {full_cmd}")
        else:
            lines.append(
                f"execute if score @s {w['progress_score']} matches {threshold + 1}.. run {full_cmd}"
            )
    return lines


def page_occupied(page_widgets: list[dict[str, Any]]) -> set[int]:
    occ: set[int] = set()
    for w in page_widgets:
        for s in occupied_slots(w):
            occ.add(s)
    return occ


def generate_page_fills(menu: dict[str, Any], out: dict[str, str]) -> None:
    slots = container_slot_count(menu["container"])
    for page in menu["pages"]:
        lines = [f"# Page {page['index']} – {page['name']}", ""]
        for w in page["widgets"]:
            lines.append(f"# slot {w['slot']}: {resolved_action_id(w)} ({w['kind']})")
            if w["kind"] == "toggle":
                lines.extend(emit_toggle(menu, w))
            elif w["kind"] == "progress":
                lines.extend(emit_progress(menu, w))
            else:
                lines.extend(emit_static(menu, w))
            lines.append("")

        occupied = page_occupied(page["widgets"])
        pads = [s for s in range(slots) if s not in occupied]
        if pads:
            lines.append("# Locked filler panes (no empty slots)")
            for s in pads:
                pad = mk_separator_widget(s)
                pad["action_id"] = f"pad_{page['index']}_{s}"
                lines.append(
                    item_replace_command(cart_selector(menu), s, pad["item"], widget_components(pad))
                )
            lines.append("")

        content = "\n".join(lines).rstrip() + "\n"
        out[f"{page_dir_path(menu)}/{page['index']}.mcfunction"] = content
