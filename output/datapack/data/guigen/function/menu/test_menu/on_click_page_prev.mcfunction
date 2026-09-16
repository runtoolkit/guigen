# Handler: page_prev (nav)

scoreboard players set @s guigen_page 0
function guigen:menu/test_menu/fill
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Page 0 – Main","italic":false,"color":"yellow"}]
