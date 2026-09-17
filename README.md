# GUI Generator

JSON → Minecraft inventory GUI datapack.

## Generate

```bash
python3 generate.py
python3 generate.py -c config/test_menu.json -o ./output/datapack
```

```
/function guigen:menu/test_menu/open
```

## Datapack layout

```
data/<ns>/function/
  core/load.mcfunction
  core/tick.mcfunction
  menu/<menu_id>/
    open.mcfunction
    close.mcfunction
    fill.mcfunction
    give_opener.mcfunction
    page/0.mcfunction …
    click/<action>.mcfunction …
data/minecraft/tags/function/{load,tick}.json
pack.mcmeta
```

## JSON highlights

Widget fields: `kind`, `slot`, `item`, `action_id`, `name`, `lore`,
`commands`, `functions`, `sound`, `condition`, **`cooldown_ticks`**, **`cost`**.

### cooldown_ticks
Blocks re-click for N ticks (`return` + scoreboard).

### cost
```json
"cost": {
  "item": "minecraft:coal",
  "count": 3,
  "score": "money",
  "amount": 10,
  "fail_message": { "text": "Not enough!", "color": "red" }
}
```
Item and/or score price deducted on success.

Containers: `chest_minecart` (27) | `hopper_minecart` (5).
