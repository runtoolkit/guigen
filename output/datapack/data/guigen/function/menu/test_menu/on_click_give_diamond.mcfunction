# Handler: give_diamond (button)

execute store result score @s guigen_tmp run clear @s minecraft:diamond 0
execute if score @s guigen_tmp matches 5.. run tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Denied: you already have 5+ diamonds.","italic":false,"color":"red"}]
execute if score @s guigen_tmp matches ..4 run give @s minecraft:diamond 1
execute if score @s guigen_tmp matches ..4 run tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"You received a diamond.","italic":false,"color":"light_purple"}]
function guigen:menu/test_menu/fill
