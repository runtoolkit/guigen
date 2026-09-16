"""
Demo menu showcasing the expanded widget + container system.

Widgets: button, label, separator, toggle, counter, nav, progress, close, confirm
Container: chest_minecart (27 slots)
"""

from models import (
    Text,
    Menu,
    Page,
    Container,
    Condition,
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


def build_test_menu() -> Menu:
    # ── Page 0 : Main ──────────────────────────────────────────────
    page0 = Page(
        index=0,
        name="Main",
        widgets=[
            label(
                1,
                "minecraft:name_tag",
                Text("— Main Menu —", color="gold", bold=True),
                lore=[Text("GUI-GENERATOR demo", color="gray")],
            ),
            confirm(
                0,
                "minecraft:compass",
                Text("Teleport to Spawn", color="aqua"),
                confirm_page=2,
                lore=[Text("Opens confirmation page", color="gray")],
                action_id="goto_confirm_tp",
            ),
            button(
                2,
                "minecraft:golden_apple",
                Text("Heal & Feed", color="green"),
                action_id="heal",
                lore=[Text("Fully restore health and hunger", color="gray")],
                commands=[
                    "effect give @s minecraft:instant_health 1 10 true",
                    "effect give @s minecraft:saturation 1 10 true",
                ],
                success_message=Text("Fully healed and fed.", color="green"),
            ),
            button(
                4,
                "minecraft:nether_star",
                Text("Give Diamond", color="light_purple"),
                action_id="give_diamond",
                lore=[Text("Only if you have < 5 diamonds", color="gray")],
                condition=Condition(
                    type="item_count_lt",
                    item="minecraft:diamond",
                    max_count=5,
                    fail_message=Text("Denied: you already have 5+ diamonds.", color="red"),
                ),
                commands=["give @s minecraft:diamond 1"],
                success_message=Text("You received a diamond.", color="light_purple"),
            ),
            separator(3),
            separator(5),
            nav(
                6,
                "minecraft:arrow",
                Text("Next Page →", color="yellow"),
                target_page=1,
                action_id="page_next",
                lore=[Text("Tools, toggles, counters", color="gray")],
                success_message=Text("Page 1 – Tools", color="yellow"),
            ),
            close_btn(8),
        ],
    )

    # ── Page 1 : Tools / Toggles / Counter / Progress ──────────────
    nv = ToggleState(
        score="guigen_toggle_nv",
        off_item="minecraft:gray_dye",
        on_item="minecraft:lime_dye",
        off_name=Text("Night Vision: OFF", color="dark_gray"),
        on_name=Text("Night Vision: ON", color="green"),
        off_lore=[Text("Shift-click to enable", color="gray")],
        on_lore=[Text("Shift-click to disable", color="gray")],
        on_commands=["effect give @s minecraft:night_vision infinite 0 true"],
        off_commands=["effect clear @s minecraft:night_vision"],
        tick_while_on=["effect give @s minecraft:night_vision infinite 0 true"],
    )

    page1 = Page(
        index=1,
        name="Tools",
        widgets=[
            label(
                1,
                "minecraft:name_tag",
                Text("— Tools & State —", color="gold", bold=True),
            ),
            toggle(0, nv, action_id="toggle_nv"),
            button(
                2,
                "minecraft:sunflower",
                Text("Set Day", color="gold"),
                action_id="set_day",
                commands=["time set day"],
                success_message=Text("Time set to day.", color="gold"),
            ),
            button(
                3,
                "minecraft:black_dye",
                Text("Set Night", color="dark_purple"),
                action_id="set_night",
                commands=["time set night"],
                success_message=Text("Time set to night.", color="dark_purple"),
            ),
            # Counter pair: − and +
            counter(
                9,
                "guigen_level",
                delta=-1,
                min_v=0,
                max_v=10,
                item="minecraft:red_concrete",
                name=Text("− Level", color="red"),
                action_id="level_dec",
            ),
            label(
                10,
                "minecraft:experience_bottle",
                Text("Level (see actionbar/chat)", color="aqua"),
                lore=[Text("Adjusted by − / + buttons", color="gray")],
            ),
            counter(
                11,
                "guigen_level",
                delta=1,
                min_v=0,
                max_v=10,
                item="minecraft:lime_concrete",
                name=Text("+ Level", color="green"),
                action_id="level_inc",
            ),
            # Progress bar driven by guigen_level (0..10 → 5 cells)
            progress(
                18,
                "guigen_level",
                width=5,
                max_v=10,
                name=Text("Level bar", color="green"),
            ),
            nav(
                6,
                "minecraft:arrow",
                Text("← Previous", color="yellow"),
                target_page=0,
                action_id="page_prev",
                success_message=Text("Page 0 – Main", color="yellow"),
            ),
            close_btn(8),
        ],
    )

    # ── Page 2 : Confirm teleport ──────────────────────────────────
    page2 = Page(
        index=2,
        name="Confirm",
        widgets=[
            label(
                1,
                "minecraft:name_tag",
                Text("Teleport to 0, 100, 0 ?", color="gold"),
            ),
            separator(0),
            separator(2),
            button(
                3,
                "minecraft:lime_concrete",
                Text("CONFIRM", color="green"),
                action_id="teleport_spawn",
                commands=[
                    "teleport @s 0 100 0",
                    "scoreboard players set @s guigen_page 0",
                ],
                success_message=Text("Teleported to spawn.", color="aqua"),
            ),
            nav(
                5,
                "minecraft:red_concrete",
                Text("CANCEL", color="red"),
                target_page=0,
                action_id="page_main",
            ),
        ],
    )

    return Menu(
        namespace="guigen",
        menu_id="test_menu",
        display_name="GUI-GENERATOR (widgets + containers)",
        timer_ticks=900,
        follow=True,
        distance_close=6.0,
        container=Container(type="chest_minecart"),
        pages=[page0, page1, page2],
        extra_scores=["guigen_level"],
    )
