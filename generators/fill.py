"""Generate fill.mcfunction + page/<n>.mcfunction."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu
from models.widgets import Widget, separator
from models.components import Text, ItemComponents
from builders.snbt import item_replace_command
from builders.paths import menu_dir, page_dir


def _cart(menu: Menu) -> str:
    return (
        f"@e[type={menu.container.entity_id},tag={menu.tag},"
        f"sort=nearest,limit=1]"
    )


def generate_fill_router(menu: Menu, out: Path) -> None:
    lines = [
        "# Auto-generated – route to current page (every slot is overwritten)",
        "",
    ]
    for page in menu.pages:
        lines.append(
            f"execute if score @s guigen_page matches {page.index} "
            f"run function {menu.page_prefix}/{page.index}"
        )
    (menu_dir(out, menu) / "fill.mcfunction").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _emit_static(menu: Menu, w: Widget) -> list[str]:
    return [item_replace_command(_cart(menu), w.slot, w.item, w.components())]


def _emit_toggle(menu: Menu, w: Widget) -> list[str]:
    assert w.toggle is not None
    lines = []
    for state in (0, 1):
        item, comps = w.components_for_toggle(state)
        cmd = item_replace_command(_cart(menu), w.slot, item, comps)
        lines.append(
            f"execute if score @s {w.toggle.score} matches {state} run {cmd}"
        )
    return lines


def _emit_progress(menu: Menu, w: Widget) -> list[str]:
    assert w.progress_score and w.progress_width and w.progress_max
    lines = []
    width = w.progress_width
    mx = w.progress_max
    for i in range(width):
        slot = w.slot + i
        threshold = (i * mx) // width
        empty_comps = ItemComponents(
            custom_name=w.name or Text(" "),
            custom_data=w.gui_custom_data(cell_slot=slot),
        )
        full_comps = ItemComponents(
            custom_name=w.name or Text(" "),
            custom_data=w.gui_custom_data(cell_slot=slot),
        )
        empty_cmd = item_replace_command(_cart(menu), slot, w.progress_empty_item, empty_comps)
        full_cmd = item_replace_command(_cart(menu), slot, w.progress_full_item, full_comps)
        lines.append(empty_cmd)
        if i == 0:
            lines.append(
                f"execute if score @s {w.progress_score} matches 1.. run {full_cmd}"
            )
        else:
            lines.append(
                f"execute if score @s {w.progress_score} matches {threshold + 1}.. run {full_cmd}"
            )
    return lines


def _page_occupied(page_widgets: list[Widget]) -> set[int]:
    occ: set[int] = set()
    for w in page_widgets:
        occ.update(w.occupied_slots())
    return occ


def generate_page_fills(menu: Menu, out: Path) -> None:
    slots = menu.container.slot_count
    pdir = page_dir(out, menu)
    for page in menu.pages:
        lines = [f"# Page {page.index} – {page.name}", ""]
        for w in page.widgets:
            lines.append(f"# slot {w.slot}: {w.resolved_action_id()} ({w.kind})")
            if w.kind == "toggle":
                lines.extend(_emit_toggle(menu, w))
            elif w.kind == "progress":
                lines.extend(_emit_progress(menu, w))
            else:
                lines.extend(_emit_static(menu, w))
            lines.append("")

        occupied = _page_occupied(page.widgets)
        pads = [s for s in range(slots) if s not in occupied]
        if pads:
            lines.append("# Locked filler panes (no empty slots)")
            for s in pads:
                pad = separator(s)
                pad.action_id = f"pad_{page.index}_{s}"
                lines.append(item_replace_command(_cart(menu), s, pad.item, pad.components()))
            lines.append("")

        (pdir / f"{page.index}.mcfunction").write_text(
            "\n".join(lines).rstrip() + "\n", encoding="utf-8"
        )
