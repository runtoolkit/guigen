"""
Widget system for the GUI generator.

Widgets are the building blocks placed into container slots.
Names / lore are always Text objects → SNBT objects (never stringified JSON).

Every GUI item carries unique custom_data:

    custom_data={guigen:{widget:1,type:"button",id:"heal"}}

`type` is the widget kind; `id` is unique per action/slot. Tick `clear`
commands match these fields (any item id) so stolen / shift-clicked widgets
are always removed from the player.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal

from .components import Text, ItemComponents


# ---------------------------------------------------------------------------
# Shared pieces
# ---------------------------------------------------------------------------

ConditionType = Literal["item_count_lt", "item_count_gte", "score", "has_tag", "gamemode"]


@dataclass
class Condition:
    type: ConditionType
    item: str | None = None
    max_count: int | None = None
    min_count: int | None = None
    score: str | None = None
    matches: str | None = None       # e.g. "0", "1..", "..5"
    tag: str | None = None
    gamemode: str | None = None
    fail_message: Text | None = None


@dataclass
class ToggleState:
    score: str
    off_item: str
    on_item: str
    off_name: Text
    on_name: Text
    off_lore: list[Text] = field(default_factory=list)
    on_lore: list[Text] = field(default_factory=list)
    on_commands: list[str] = field(default_factory=list)
    off_commands: list[str] = field(default_factory=list)
    tick_while_on: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Widget base + concrete types
# ---------------------------------------------------------------------------

WidgetKind = Literal[
    "button",      # classic clickable
    "label",       # display-only (not clickable / no action)
    "separator",   # filler pane
    "toggle",      # on/off with two visuals
    "counter",     # +/- score stepper
    "nav",         # page change
    "progress",    # multi-slot bar driven by a score
    "close",       # close menu
    "confirm",     # jump to a confirm page
]


@dataclass
class Widget:
    """Base fields shared by every widget."""
    slot: int
    kind: WidgetKind
    item: str = "minecraft:stone"
    action_id: str = ""
    name: Text | None = None
    lore: list[Text] = field(default_factory=list)
    # optional shared behaviour
    commands: list[str] = field(default_factory=list)
    success_message: Text | None = None
    condition: Condition | None = None
    # type-specific
    toggle: ToggleState | None = None
    target_page: int | None = None
    confirm_page: int | None = None
    # counter
    counter_score: str | None = None
    counter_delta: int = 1
    counter_min: int = 0
    counter_max: int = 64
    counter_display_item: str | None = None  # middle display slot item
    # progress bar (occupies slot..slot+width-1)
    progress_score: str | None = None
    progress_max: int = 10
    progress_width: int = 5
    progress_full_item: str = "minecraft:lime_stained_glass_pane"
    progress_empty_item: str = "minecraft:gray_stained_glass_pane"
    # label / separator
    clickable: bool = True

    def resolved_action_id(self) -> str:
        if self.action_id:
            return self.action_id
        return f"{self.kind}_{self.slot}"

    def occupied_slots(self) -> list[int]:
        if self.kind == "progress":
            return list(range(self.slot, self.slot + max(1, self.progress_width)))
        return [self.slot]

    def gui_custom_data(self, *, cell_slot: int | None = None) -> dict[str, Any]:
        """Unique per-widget (and per progress cell) custom_data payload."""
        wid = self.resolved_action_id()
        if cell_slot is not None:
            wid = f"{wid}_s{cell_slot}"
        return {
            "guigen": {
                "widget": 1,
                "type": self.kind,
                "id": wid,
            }
        }

    def components(self, action: str | None = None, *, cell_slot: int | None = None) -> ItemComponents:
        # `action` kept for call-site compat; id always comes from resolved_action_id
        _ = action
        return ItemComponents(
            custom_name=self.name,
            lore=list(self.lore),
            custom_data=self.gui_custom_data(cell_slot=cell_slot),
        )

    def components_for_toggle(self, state: int) -> tuple[str, ItemComponents]:
        assert self.toggle is not None
        t = self.toggle
        data = self.gui_custom_data()
        if state == 0:
            return t.off_item, ItemComponents(
                custom_name=t.off_name,
                lore=list(t.off_lore),
                custom_data=data,
            )
        return t.on_item, ItemComponents(
            custom_name=t.on_name,
            lore=list(t.on_lore),
            custom_data=data,
        )

    def is_interactive(self) -> bool:
        return self.kind not in ("label", "separator", "progress")


# Convenience constructors ---------------------------------------------------

def button(
    slot: int,
    item: str,
    name: Text,
    *,
    action_id: str = "",
    lore: list[Text] | None = None,
    commands: list[str] | None = None,
    success_message: Text | None = None,
    condition: Condition | None = None,
) -> Widget:
    return Widget(
        slot=slot,
        kind="button",
        item=item,
        action_id=action_id or f"btn_{slot}",
        name=name,
        lore=lore or [],
        commands=commands or [],
        success_message=success_message,
        condition=condition,
    )


def label(slot: int, item: str, name: Text, lore: list[Text] | None = None) -> Widget:
    return Widget(
        slot=slot,
        kind="label",
        item=item,
        action_id=f"label_{slot}",
        name=name,
        lore=lore or [],
        clickable=False,
    )


def separator(slot: int, item: str = "minecraft:gray_stained_glass_pane") -> Widget:
    return Widget(
        slot=slot,
        kind="separator",
        item=item,
        action_id=f"separator_{slot}",
        name=Text(" ", color="dark_gray"),
        clickable=False,
    )


def toggle(
    slot: int,
    state: ToggleState,
    *,
    action_id: str = "",
) -> Widget:
    return Widget(
        slot=slot,
        kind="toggle",
        item=state.off_item,
        action_id=action_id or state.score,
        toggle=state,
        name=state.off_name,
    )


def nav(
    slot: int,
    item: str,
    name: Text,
    target_page: int,
    *,
    action_id: str = "",
    lore: list[Text] | None = None,
    success_message: Text | None = None,
) -> Widget:
    return Widget(
        slot=slot,
        kind="nav",
        item=item,
        action_id=action_id or f"nav_{target_page}",
        name=name,
        lore=lore or [],
        target_page=target_page,
        success_message=success_message,
    )


def close_btn(
    slot: int = 8,
    item: str = "minecraft:barrier",
    name: Text | None = None,
) -> Widget:
    return Widget(
        slot=slot,
        kind="close",
        item=item,
        action_id="close_menu",
        name=name or Text("Close Menu", color="red"),
        lore=[Text("Close this menu", color="gray")],
        success_message=Text("Menu closed.", color="red"),
    )


def confirm(
    slot: int,
    item: str,
    name: Text,
    confirm_page: int,
    *,
    action_id: str = "",
    lore: list[Text] | None = None,
) -> Widget:
    return Widget(
        slot=slot,
        kind="confirm",
        item=item,
        action_id=action_id or f"confirm_{slot}",
        name=name,
        lore=lore or [],
        confirm_page=confirm_page,
        success_message=Text("Confirm?", color="gold"),
    )


def counter(
    slot: int,
    score: str,
    *,
    delta: int = 1,
    min_v: int = 0,
    max_v: int = 64,
    item: str = "minecraft:stone_button",
    name: Text | None = None,
    action_id: str = "",
) -> Widget:
    """A single clickable stepper (+ or - depending on delta sign)."""
    sign = "+" if delta > 0 else "−"
    return Widget(
        slot=slot,
        kind="counter",
        item=item,
        action_id=action_id or f"counter_{score}_{'inc' if delta > 0 else 'dec'}",
        name=name or Text(f"{sign}{abs(delta)}", color="yellow"),
        lore=[Text(f"Adjust {score}", color="gray")],
        counter_score=score,
        counter_delta=delta,
        counter_min=min_v,
        counter_max=max_v,
    )


def progress(
    start_slot: int,
    score: str,
    *,
    width: int = 5,
    max_v: int = 10,
    full_item: str = "minecraft:lime_stained_glass_pane",
    empty_item: str = "minecraft:gray_stained_glass_pane",
    name: Text | None = None,
) -> Widget:
    """
    Multi-slot progress bar. Occupies start_slot .. start_slot+width-1.
    Fill level = score / max_v * width.
    """
    return Widget(
        slot=start_slot,
        kind="progress",
        item=empty_item,
        action_id=f"progress_{score}",
        name=name or Text("Progress", color="green"),
        progress_score=score,
        progress_max=max_v,
        progress_width=width,
        progress_full_item=full_item,
        progress_empty_item=empty_item,
        clickable=False,
    )
