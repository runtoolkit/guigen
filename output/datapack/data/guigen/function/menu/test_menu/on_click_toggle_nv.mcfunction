# Handler: toggle_nv (toggle)

execute if score @s guigen_toggle_nv matches 1 run scoreboard players set @s guigen_tmp 1
execute if score @s guigen_toggle_nv matches 0 run scoreboard players set @s guigen_toggle_nv 1
execute if score @s guigen_tmp matches 1 run scoreboard players set @s guigen_toggle_nv 0
scoreboard players reset @s guigen_tmp

execute if score @s guigen_toggle_nv matches 1 run effect give @s minecraft:night_vision infinite 0 true
execute if score @s guigen_toggle_nv matches 0 run effect clear @s minecraft:night_vision

execute if score @s guigen_toggle_nv matches 1 run tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Night Vision: ON","italic":false,"color":"green"}]
execute if score @s guigen_toggle_nv matches 0 run tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Night Vision: OFF","italic":false,"color":"dark_gray"}]
function guigen:menu/test_menu/fill
