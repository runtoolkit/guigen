"""Menu, Page and Container definitions."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

from .widgets import Widget


ContainerType = Literal["chest_minecart", "hopper_minecart"]


@dataclass
class Container:
    """
    Physical container that holds the GUI slots.
    chest_minecart : 27 slots, follows player
    hopper_minecart: 5 slots, compact UI
    """
    type: ContainerType = "chest_minecart"
    invulnerable: bool = True
    no_gravity: bool = True
    silent: bool = True

    @property
    def entity_id(self) -> str:
        return f"minecraft:{self.type}"

    @property
    def slot_count(self) -> int:
        return 5 if self.type == "hopper_minecart" else 27

    def summon_nbt(self, tags: list[str]) -> str:
        tag_list = ",".join(f'"{t}"' for t in tags)
        flags = []
        if self.invulnerable:
            flags.append("Invulnerable:1b")
        if self.no_gravity:
            flags.append("NoGravity:1b")
        if self.silent:
            flags.append("Silent:1b")
        flags.append(f"Tags:[{tag_list}]")
        return "{" + ",".join(flags) + "}"


@dataclass
class Page:
    index: int
    name: str
    widgets: list[Widget] = field(default_factory=list)

    # backward-compat alias
    @property
    def buttons(self) -> list[Widget]:
        return self.widgets


@dataclass
class Menu:
    """One complete GUI menu."""
    namespace: str
    menu_id: str
    display_name: str = "GUI Menu"
    timer_ticks: int = 900
    follow: bool = True
    distance_close: float = 6.0
    container: Container = field(default_factory=Container)
    pages: list[Page] = field(default_factory=list)
    extra_scores: list[str] = field(default_factory=list)

    @property
    def function_prefix(self) -> str:
        return f"{self.namespace}:menu/{self.menu_id}"

    @property
    def tag(self) -> str:
        return f"{self.namespace}.{self.menu_id}"

    def all_widgets(self) -> list[Widget]:
        result: list[Widget] = []
        for p in self.pages:
            result.extend(p.widgets)
        return result

    # backward-compat
    def all_buttons(self) -> list[Widget]:
        return self.all_widgets()

    def interactive_widgets(self) -> list[Widget]:
        return [w for w in self.all_widgets() if w.is_interactive()]

    def collect_scores(self) -> list[str]:
        scores = ["guigen_menu_timer", "guigen_click", "guigen_page", "guigen_tmp"]
        scores.extend(self.extra_scores)
        for w in self.all_widgets():
            if w.toggle and w.toggle.score not in scores:
                scores.append(w.toggle.score)
            if w.counter_score and w.counter_score not in scores:
                scores.append(w.counter_score)
            if w.progress_score and w.progress_score not in scores:
                scores.append(w.progress_score)
        return scores
