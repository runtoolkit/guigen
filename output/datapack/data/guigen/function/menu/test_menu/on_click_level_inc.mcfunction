# Handler: level_inc (counter)

scoreboard players add @s guigen_level 1
execute if score @s guigen_level matches 11.. run scoreboard players set @s guigen_level 10
execute if score @s guigen_level matches ..-1 run scoreboard players set @s guigen_level 0
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"guigen_level = ","color":"yellow"},{"score":{"name":"@s","objective":"guigen_level"},"color":"gold"}]
function guigen:menu/test_menu/fill
