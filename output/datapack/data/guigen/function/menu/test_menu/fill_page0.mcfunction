# Page 0 – Main

# slot 1: label_1 (label)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.1 with minecraft:name_tag[custom_name={text:"— Main Menu —",italic:false,color:"gold",bold:true},lore=[{text:"GUI-GENERATOR demo",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"label",id:"label_1"}},max_stack_size=1]

# slot 0: goto_confirm_tp (confirm)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.0 with minecraft:compass[custom_name={text:"Teleport to Spawn",italic:false,color:"aqua"},lore=[{text:"Opens confirmation page",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"confirm",id:"goto_confirm_tp"}},max_stack_size=1]

# slot 2: heal (button)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.2 with minecraft:golden_apple[custom_name={text:"Heal & Feed",italic:false,color:"green"},lore=[{text:"Fully restore health and hunger",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"button",id:"heal"}},max_stack_size=1]

# slot 4: give_diamond (button)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.4 with minecraft:nether_star[custom_name={text:"Give Diamond",italic:false,color:"light_purple"},lore=[{text:"Only if you have < 5 diamonds",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"button",id:"give_diamond"}},max_stack_size=1]

# slot 3: separator_3 (separator)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.3 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"separator_3"}},max_stack_size=1]

# slot 5: separator_5 (separator)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.5 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"separator_5"}},max_stack_size=1]

# slot 6: page_next (nav)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.6 with minecraft:arrow[custom_name={text:"Next Page →",italic:false,color:"yellow"},lore=[{text:"Tools, toggles, counters",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"nav",id:"page_next"}},max_stack_size=1]

# slot 8: close_menu (close)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.8 with minecraft:barrier[custom_name={text:"Close Menu",italic:false,color:"red"},lore=[{text:"Close this menu",italic:false,color:"gray"}],custom_data={guigen:{widget:1,type:"close",id:"close_menu"}},max_stack_size=1]

# Locked filler panes (no empty slots)
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.7 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_7"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.9 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_9"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.10 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_10"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.11 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_11"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.12 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_12"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.13 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_13"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.14 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_14"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.15 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_15"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.16 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_16"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.17 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_17"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.18 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_18"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.19 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_19"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.20 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_20"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.21 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_21"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.22 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_22"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.23 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_23"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.24 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_24"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.25 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_25"}},max_stack_size=1]
item replace entity @e[type=minecraft:chest_minecart,tag=guigen.test_menu,sort=nearest,limit=1] container.26 with minecraft:gray_stained_glass_pane[custom_name={text:" ",italic:false,color:"dark_gray"},custom_data={guigen:{widget:1,type:"separator",id:"pad_0_26"}},max_stack_size=1]
