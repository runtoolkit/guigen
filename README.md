# GUI Generator

Declarative Minecraft inventory-GUI datapack generator.

## Components are objects (never stringified JSON)

```
custom_name={text:"Heal & Feed",italic:false,color:"green"}
lore=[{text:"...",italic:false,color:"gray"}]
custom_data={guigen:{widget:1,type:"button",id:"heal"}}
max_stack_size=1
```

Every widget item carries unique `custom_data`:

| Field    | Meaning                                      |
|----------|----------------------------------------------|
| `widget` | `1` – GUI item (opener book does **not** have this) |
| `type`   | Widget kind (`button`, `label`, `toggle`, …) |
| `id`     | Unique action / slot id                      |

Tick `clear` commands match `type` + `id` (item id is ignored), so taking a
widget out of the cart always vacuums it from the player and the layout is
restored next tick. Unused slots are filled with locked separator panes.

## Layout

```
gui_generator/
  models/
    components.py   Text, ItemComponents
    widgets.py      Widget + constructors (button, label, toggle, …)
    menu.py         Menu, Page, Container
  builders/         SNBT emission, paths
  generators/       fill, handlers, tick, lifecycle
  config/           menu definitions
  generate.py
```

## Widget types

| Widget      | Role                                      |
|-------------|-------------------------------------------|
| `button`    | Click → commands (optional condition)     |
| `label`     | Display-only                              |
| `separator` | Filler pane                               |
| `toggle`    | On/off with two visuals + tick keep-alive |
| `counter`   | ± score stepper with clamp                |
| `nav`       | Change page                               |
| `progress`  | Multi-slot bar driven by a score          |
| `close`     | Close menu                                |
| `confirm`   | Jump to a confirmation page               |

## Container types

| Type              | Slots | Notes                |
|-------------------|-------|----------------------|
| `chest_minecart`  | 27    | Default, follows you |
| `hopper_minecart` | 5     | Compact UI           |

## Usage

```bash
python3 generate.py
python3 generate.py --out /path/to/datapack
```

```
/function guigen:menu/test_menu/open
```
