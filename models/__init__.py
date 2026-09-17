from .components import Text, ItemComponents
from .widgets import (
    Widget,
    Condition,
    Cost,
    ToggleState,
    button,
    label,
    separator,
    toggle,
    nav,
    close_btn,
    confirm,
    counter,
    progress,
)
from .menu import Menu, Page, Container
from .loader import load_menu, menu_from_dict

Button = Widget

__all__ = [
    "Text",
    "ItemComponents",
    "Widget",
    "Button",
    "Condition",
    "Cost",
    "ToggleState",
    "button",
    "label",
    "separator",
    "toggle",
    "nav",
    "close_btn",
    "confirm",
    "counter",
    "progress",
    "Menu",
    "Page",
    "Container",
    "load_menu",
    "menu_from_dict",
]
