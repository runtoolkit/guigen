# Auto-generated load
scoreboard objectives add guigen_menu_timer dummy
scoreboard objectives add guigen_click dummy
scoreboard objectives add guigen_page dummy
scoreboard objectives add guigen_tmp dummy
scoreboard objectives add guigen_level dummy
scoreboard objectives add guigen_toggle_nv dummy

execute as @e[type=minecraft:chest_minecart,tag=guigen.test_menu] run data modify entity @s Items set value []
kill @e[type=minecraft:chest_minecart,tag=guigen.test_menu]

tellraw @a [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Loaded. /function guigen:menu/test_menu/open","color":"green"}]
