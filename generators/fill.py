"""Generate fill.mcfunction + fill_pageN.mcfunction."""

from __future__ import annotations
from pathlib import Path

from models.menu import Menu
from models.widgets import Widget
from models.components import Text, ItemComponents
from builders.snbt import item_replace_command
from builders.paths import menu_dir


def _cart(menu: Menu) -> str:
    return (
        f'@e[type={menu.container.entity_id},tag={menu.tag},'
        f'distance=..8,sort=nearest,limit=1]'
    )


def generate_fill_router(menu: Menu, out: Path) -> None:
    lines = [
        "# Auto-generated – clear slots then route to current page",
        f"execute as {_cart(menu)} run data modify entity @s Items set value []",
        "",
    ]
    for page in menu.pages:
        lines.append(
            f"execute if score @s guigen_page matches {page.index} "
            f"run function {menu.function_prefix}/fill_page{page.index}"
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
    """
    For each cell i in [0, width):
      if score >= (i+1)/width * max  → full item else empty item
    Approximate with integer thresholds.
    """
    assert w.progress_score and w.progress_width and w.progress_max
    lines = []
    width = w.progress_width
    mx = w.progress_max
    for i in range(width):
        slot = w.slot + i
        # threshold: cell i is full when score >= ceil((i+1)*max/width)
        # use: score >= (i * max // width) + 1  roughly
        threshold = (i * mx) // width
        # empty by default
        empty_comps = ItemComponents(
            custom_name=w.name or Text(" "),
            custom_data={"guigen": {"ui": 1}},
        )
        full_comps = ItemComponents(
            custom_name=w.name or Text(" "),
            custom_data={"guigen": {"ui": 1}},
        )
        empty_cmd = item_replace_command(_cart(menu), slot, w.progress_empty_item, empty_comps)
        full_cmd = item_replace_command(_cart(menu), slot, w.progress_full_item, full_comps)
        # always place empty first, then override with full if score high enough
        lines.append(empty_cmd)
        if i == 0:
            # first cell full when score >= 1
            lines.append(
                f"execute if score @s {w.progress_score} matches 1.. run {full_cmd}"
            )
        else:
            lines.append(
                f"execute if score @s {w.progress_score} matches {threshold + 1}.. run {full_cmd}"
            )
    return lines


def _emit_counter_display(menu: Menu, w: Widget) -> list[str]:
    """Counter widget itself is the clickable +/- ; display is optional via label."""
    return _emit_static(menu, w)


def generate_page_fills(menu: Menu, out: Path) -> None:
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
        path = menu_dir(out, menu) / f"fill_page{page.index}.mcfunction"
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
