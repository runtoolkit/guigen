"""Non-fatal validation warnings (UI-only helper from the web version)."""

from __future__ import annotations

from typing import Any

from .models import (
    all_widgets,
    container_slot_count,
    interactive_widgets,
    occupied_slots,
    resolved_action_id,
)


def validate_menu(menu: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    slot_count = container_slot_count(menu["container"])

    for page in menu["pages"]:
        by_slot: dict[int, list[dict[str, Any]]] = {}
        for w in page["widgets"]:
            for s in occupied_slots(w):
                by_slot.setdefault(s, []).append(w)
                if s < 0 or s >= slot_count:
                    warnings.append(
                        f"Page {page['index']} ({page['name']}): slot {s} is out of range "
                        f"for {menu['container']['type']} (valid: 0–{slot_count - 1})."
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
