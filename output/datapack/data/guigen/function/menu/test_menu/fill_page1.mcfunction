# Page 1 – Tools

# slot 1: label_1 (label)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.1 with minecraft:name_tag[custom_name={text:"— Tools & State —",italic:false,color:"gold",bold:true},custom_data={guigen:{widget:1,type:"label",id:"label_1"}},max_stack_size=1]

# slot 0: toggle_nv (toggle)
execute if score @s guigen_toggle_nv matches 0 run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.0 with minecraft:gray_dye[custom_name={text:"Night Vision: OFF",italic:false,color:"dark_gray"},lore=[{text:"Shift-click to enable",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"toggle",id:"toggle_nv"}},max_stack_size=1]
execute if score @s guigen_toggle_nv matches 1 run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.0 with minecraft:lime_dye[custom_name={text:"Night Vision: ON",italic:false,color:"green"},lore=[{text:"Shift-click to disable",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"toggle",id:"toggle_nv"}},max_stack_size=1]

# slot 2: set_day (button)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.2 with minecraft:sunflower[custom_name={text:"Set Day",italic:false,color:"gold"},custom_data={guigen:{widget:1,type:"button",id:"set_day"}},max_stack_size=1]

# slot 3: set_night (button)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.3 with minecraft:black_dye[custom_name={text:"Set Night",italic:false,color:"dark_purple"},custom_data={guigen:{widget:1,type:"button",id:"set_night"}},max_stack_size=1]

# slot 9: level_dec (counter)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.9 with minecraft:red_concrete[custom_name={text:"− Level",italic:false,color:"red"},lore=[{text:"Adjust guigen_level",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"counter",id:"level_dec"}},max_stack_size=1]

# slot 10: label_10 (label)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.10 with minecraft:experience_bottle[custom_name={text:"Level (see actionbar/chat)",italic:false,color:"aqua"},lore=[{text:"Adjusted by − / + buttons",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"label",id:"label_10"}},max_stack_size=1]

# slot 11: level_inc (counter)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.11 with minecraft:lime_concrete[custom_name={text:"+ Level",italic:false,color:"green"},lore=[{text:"Adjust guigen_level",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"counter",id:"level_inc"}},max_stack_size=1]

# slot 18: progress_guigen_level (progress)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.18 with minecraft:gray_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s18"}},max_stack_size=1]
execute if score @s guigen_level matches 1.. run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.18 with minecraft:lime_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s18"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.19 with minecraft:gray_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s19"}},max_stack_size=1]
execute if score @s guigen_level matches 3.. run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.19 with minecraft:lime_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s19"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.20 with minecraft:gray_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s20"}},max_stack_size=1]
execute if score @s guigen_level matches 5.. run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.20 with minecraft:lime_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s20"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.21 with minecraft:gray_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s21"}},max_stack_size=1]
execute if score @s guigen_level matches 7.. run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.21 with minecraft:lime_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s21"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.22 with minecraft:gray_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s22"}},max_stack_size=1]
execute if score @s guigen_level matches 9.. run item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.22 with minecraft:lime_stained_glass_pane[custom_name={text:"Level bar",italic:false,color:"green"},custom_data={guigen:{widget:1,type:"progress",id:"progress_guigen_level_s22"}},max_stack_size=1]

# slot 6: page_prev (nav)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.6 with minecraft:arrow[custom_name={text:"← Previous",italic:false,color:"yellow"},custom_data={guigen:{widget:1,type:"nav",id:"page_prev"}},max_stack_size=1]

# slot 8: close_menu (close)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.8 with minecraft:barrier[custom_name={text:"Close Menu",italic:false,color:"red"},lore=[{text:"Close this menu",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"close",id:"close_menu"}},max_stack_size=1]

# Locked filler panes (no empty slots)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.4 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_4"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.5 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_5"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.7 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_7"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.12 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_12"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.13 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_13"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.14 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_14"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.15 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_15"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.16 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_16"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.17 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_17"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.23 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_23"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.24 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_24"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.25 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_25"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.26 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_1_26"}},max_stack_size=1]
