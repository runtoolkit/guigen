# Handler: teleport_spawn (button)

teleport @s 0 100 0
scoreboard players set @s guigen_page 0
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Teleported to spawn.","italic":false,"color":"aqua"}]
function guigen:menu/test_menu/fill
