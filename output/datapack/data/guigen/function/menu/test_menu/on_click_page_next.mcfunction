# Handler: page_next (nav)

scoreboard players set @s guigen_page 1
function guigen:menu/test_menu/fill
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Page 1 – Tools","italic":false,"color":"yellow"}]
