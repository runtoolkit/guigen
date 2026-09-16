# Auto-generated open
function guigen:menu/test_menu/close

summon minecraft:chest_minecart ~ ~ ~ {Invulnerable:1b,NoGravity:1b,Silent:1b,CustomNameVisible:0b,CustomName={text:"GUI-GENERATOR (widgets + containers)",italic:false},Tags:["guigen.menu","guigen.test_menu"]}

scoreboard players set @s guigen_page 0
execute unless score @s guigen_toggle_nv matches 0.. run scoreboard players set @s guigen_toggle_nv 0
execute unless score @s guigen_level matches 0.. run scoreboard players set @s guigen_level 0
function guigen:menu/test_menu/fill
scoreboard players set @s guigen_menu_timer 900

tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Menu opened. Right-click the cart, then SHIFT-click buttons.","color":"yellow"}]
