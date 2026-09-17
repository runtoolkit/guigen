# GUI Generator

Declarative Minecraft inventory-GUI datapack generator.

Menus are defined in **JSON**. Run the generator to emit a ready-to-use datapack.

## Quick start

```bash
python3 generate.py
python3 generate.py --config config/test_menu.json --out ./output/datapack
```

In-game:

```
/reload
/function guigen:menu/test_menu/open
```

## JSON config

See `config/test_menu.json` for a full demo.

### Top-level fields

| Field | Default | Description |
|-------|---------|-------------|
| `namespace` | required | Datapack namespace |
| `menu_id` | required | Menu folder name |
| `display_name` | `menu_id` | Cart inventory title |
| `timer_ticks` | `900` | Auto-close timer |
| `follow` | `true` | Teleport cart to player each tick |
| `container.type` | `chest_minecart` | `chest_minecart` (27) or `hopper_minecart` (5) |
| `extra_scores` | `[]` | Extra scoreboard objectives |
| `pack_description` | auto | pack.mcmeta description |
| `opener_name` / `opener_lore` | defaults | Knowledge-book opener text |

### Widget kinds

| kind | Role |
|------|------|
| `button` | Click → commands / functions |
| `label` | Display-only |
| `separator` / `filler` / `pad` | Locked pane |
| `toggle` | On/off score + two visuals |
| `counter` / `stepper` | ± score with clamp |
| `nav` / `page` | Change page |
| `progress` / `bar` | Multi-slot score bar |
| `close` | Close menu |
| `confirm` | Jump to confirm page |

### Shared widget fields

- `slot`, `item`, `action_id`
- `name`, `lore` — `{ "text", "color", "bold", "italic" }`
- `commands` — raw command lines
- `functions` — datapack functions (`namespace:path`)
- `sound` — playsound id on click
- `success_message`, `condition`

### Conditions

`item_count_lt`, `item_count_gte`, `score`, `has_tag`, `gamemode`

Every GUI item gets:

```
custom_data={guigen:{widget:1,type:"button",id:"heal"}}
```

Empty slots are padded; layout restores every tick; clear matches type+id.
