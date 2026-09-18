"""Non-fatal validation warnings."""

from __future__ import annotations

from typing import Any

from .models import (
    LAYOUT_PRESETS,
    VALID_CONTAINER_TYPES,
    all_widgets,
    container_slot_count,
    interactive_widgets,
    occupied_slots,
    resolved_action_id,
)


def validate_menu(menu: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    slot_count = container_slot_count(menu["container"])
    ctype = menu["container"]["type"]

    if ctype not in VALID_CONTAINER_TYPES:
        warnings.append(
            f"Container type '{ctype}' is not in the known list: {', '.join(VALID_CONTAINER_TYPES)}."
        )

    layout = menu.get("layout")
    if layout and str(layout) not in LAYOUT_PRESETS:
        warnings.append(
            f"Unknown menu layout '{layout}'. Known: {', '.join(LAYOUT_PRESETS)}."
        )

    y_off = float(menu["container"].get("y_offset") or 0.0)
    if abs(y_off) > 5:
        warnings.append(
            f"container.y_offset={y_off} is unusually large; the cart may be hard to click."
        )

    for page in menu["pages"]:
        page_layout = page.get("layout")
        if page_layout and str(page_layout) not in LAYOUT_PRESETS:
            warnings.append(
                f"Page {page['index']} ({page['name']}): unknown layout '{page_layout}'. "
                f"Known: {', '.join(LAYOUT_PRESETS)}."
            )

        by_slot: dict[int, list[dict[str, Any]]] = {}
        for w in page["widgets"]:
            for s in occupied_slots(w):
                by_slot.setdefault(s, []).append(w)
                if s < 0 or s >= slot_count:
                    warnings.append(
                        f"Page {page['index']} ({page['name']}): slot {s} is out of range "
                        f"for {ctype} (valid: 0–{slot_count - 1})."
                    )
        for slot, widgets in by_slot.items():
            if len(widgets) > 1:
                names = ", ".join(resolved_action_id(w) for w in widgets)
                warnings.append(
                    f"Page {page['index']} ({page['name']}): slot {slot} is claimed by "
                    f"{len(widgets)} widgets ({names}) — only the last one placed will actually show."
                )

    valid_indices = {p["index"] for p in menu["pages"]}
    for w in all_widgets(menu):
        if w["kind"] == "nav" and w.get("target_page") not in valid_indices:
            warnings.append(
                f'Widget "{resolved_action_id(w)}" (nav) targets page {w.get("target_page")}, '
                f"which does not exist. Valid pages: {', '.join(str(i) for i in sorted(valid_indices))}."
            )
        if w["kind"] == "confirm" and w.get("confirm_page") not in valid_indices:
            warnings.append(
                f'Widget "{resolved_action_id(w)}" (confirm) targets page {w.get("confirm_page")}, '
                f"which does not exist. Valid pages: {', '.join(str(i) for i in sorted(valid_indices))}."
            )
        if w.get("count", 1) > 64:
            warnings.append(
                f'Widget "{resolved_action_id(w)}" has count={w.get("count")} (>64).'
            )
        if w["kind"] == "link" and not w.get("url"):
            warnings.append(
                f'Widget "{resolved_action_id(w)}" (link) has no url — click will do nothing useful.'
            )
        if w["kind"] == "cycle":
            opts = (w.get("cycle") or {}).get("options") or []
            if len(opts) < 2:
                warnings.append(
                    f'Widget "{resolved_action_id(w)}" (cycle) needs at least 2 options.'
                )

    seen_action_ids: dict[str, list[dict[str, Any]]] = {}
    for w in interactive_widgets(menu):
        aid = resolved_action_id(w)
        seen_action_ids.setdefault(aid, []).append(w)
    for aid, widgets in seen_action_ids.items():
        if len(widgets) > 1:
            warnings.append(
                f'action_id "{aid}" is reused by {len(widgets)} widgets — only the first widget\'s '
                f"click behavior is generated; the rest will trigger that same handler regardless "
                f"of their own commands."
            )

    return warnings
