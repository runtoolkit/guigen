# Auto-generated tick
# Timer
execute as @a[scores={guigen_menu_timer=1..}] run scoreboard players remove @s guigen_menu_timer 1
execute as @a[scores={guigen_menu_timer=0}] at @s run function guigen:menu/test_menu/close

# Follow: always tp tagged cart onto the player (no distance filter)
execute as @a[scores={guigen_menu_timer=1..}] at @s as @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] run tp @s ~ ~ ~
execute as @a[scores={guigen_menu_timer=1..}] at @s unless entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,limit=1] run function guigen:menu/test_menu/close

execute as @a[scores={guigen_toggle_nv=1}] run effect give @s minecraft:night_vision infinite 0 true

# Click detection – clear by custom_data type+id (any item id)

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"confirm",id:"goto_confirm_tp"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_goto_confirm_tp
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"button",id:"heal"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_heal
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"button",id:"give_diamond"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_give_diamond
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"nav",id:"page_next"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_page_next
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"close",id:"close_menu"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_close_menu
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"toggle",id:"toggle_nv"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_toggle_nv
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"button",id:"set_day"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_set_day
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"button",id:"set_night"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_set_night
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"counter",id:"level_dec"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_level_dec
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"counter",id:"level_inc"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_level_inc
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"nav",id:"page_prev"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_page_prev
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"button",id:"teleport_spawn"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_teleport_spawn
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

execute as @a[scores={guigen_menu_timer=1..}] store success score @s guigen_click run clear @s *[custom_data~{guigen:{type:"nav",id:"page_main"}}] 1
execute as @a[scores={guigen_click=1}] at @s run function guigen:menu/test_menu/on_click_page_main
scoreboard players reset @a[scores={guigen_click=1}] guigen_click

# Vacuum every GUI widget from the player (display + leftovers + cursor)

execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{type:"label"}}]
execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{type:"separator"}}]
execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{type:"progress"}}]
execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{widget:1}}]
execute as @a[scores={guigen_menu_timer=1..}] run clear @s *[custom_data~{guigen:{widget:1}}]

# Restore full layout every tick
execute as @a[scores={guigen_menu_timer=1..}] at @s run function guigen:menu/test_menu/fill

# Kill dropped GUI items
kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{guigen:{widget:1}}}}}]
kill @e[type=minecraft:item,nbt={Item:{components:{custom_data:{guigen:{widget:1}}}}}]
