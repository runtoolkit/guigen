# Handler: goto_confirm_tp (confirm)

scoreboard players set @s guigen_page 2
function guigen:menu/test_menu/fill
tellraw @s [{"text":"[GUI-GENERATOR] ","color":"gray"},{"text":"Confirm?","italic":false,"color":"gold"}]
