# ● guigenmc

**JSON → Minecraft GUI datapack** generator.

- **CLI** — generate from a config file in the terminal  
- **Web UI** — visual editor in your browser  

Works on **Linux**, **macOS**, **GitHub Codespaces**, and **GitHub Actions**.  
No extra packages — Python 3.9+ only.

---

## Quick start

```bash
pip install -e .

# Visual editor (browser)
guigenmc ui

# Or from a JSON file
guigenmc generate my_menu.json
guigenmc generate my_menu.json -z    # zip
```

In Minecraft:

1. Put the datapack folder in `world/datapacks/`
2. `/reload`
3. `/function <namespace>:menu/<menu_id>/open`
4. Right-click the minecart → **SHIFT-click** buttons

---

## Commands

| Command | What it does |
|---------|--------------|
| `guigenmc ui` | Open the visual web editor |
| `guigenmc generate config.json` | Build datapack folder |
| `guigenmc generate config.json -z` | Build a `.zip` |
| `guigenmc generate config.json -o name` | Custom output name |
| `guigenmc generate config.json -f` | Overwrite existing |
| `guigenmc validate config.json` | Check errors / warnings |
| `guigenmc tree config.json` | Preview file list (no write) |
| `guigenmc -h` | Help |

Aliases: `guigenmc gen`, `guigenmc g`, `guigenmc check`.

### UI options

```bash
guigenmc ui                  # http://127.0.0.1:8765
guigenmc ui -p 9000          # custom port
guigenmc ui --host 0.0.0.0   # Codespaces / remote access
guigenmc ui --no-open        # don't open browser
```

In Codespaces: use `--host 0.0.0.0` and open the forwarded port in the browser.

---

## Colors

Colored terminal output is on by default.

- Off: `NO_COLOR=1 guigenmc generate …`
- Force on: `FORCE_COLOR=1 guigenmc generate …`

---

## GitHub Actions example

```yaml
name: Build datapack
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e .
      - run: guigenmc generate my_menu.json -z -o datapack.zip
      - uses: actions/upload-artifact@v4
        with:
          name: datapack
          path: datapack.zip
```

---

## Config basics

Minimal `config.json`:

```json
{
  "namespace": "mymod",
  "menu_id": "shop",
  "pages": [
    {
      "index": 0,
      "name": "Main",
      "widgets": [
        {
          "kind": "button",
          "slot": 13,
          "item": "minecraft:diamond",
          "name": { "text": "Get Diamond", "color": "aqua" },
          "commands": ["give @s minecraft:diamond 1"]
        },
        { "kind": "close", "slot": 26 }
      ]
    }
  ]
}
```

### Widget kinds

| kind | Description |
|------|-------------|
| `button` | Runs commands / functions on click |
| `label` | Display-only item |
| `separator` | Filler pane |
| `toggle` | On/off switch with score |
| `counter` | +/− a scoreboard value |
| `progress` | Multi-slot progress bar |
| `nav` | Go to another page |
| `confirm` | Go to a confirm page |
| `close` | Close the menu |
| `random` | Weighted random rewards |

Also supports: cost, cooldown, conditions, sounds, multi-page menus, hopper/chest minecart containers.

---

## Requirements

- Python **3.9+**
- Nothing else (stdlib only)

---

## License

MIT
