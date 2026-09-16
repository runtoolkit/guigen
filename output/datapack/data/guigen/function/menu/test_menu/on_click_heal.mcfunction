# Handler: heal (button)

effect give @s minecraft:instant_health 1 10 true
effect give @s minecraft:saturation 1 10 true
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Fully healed and fed.","italic":false,"color":"green"}]
function guigen:menu/test_menu/fill
