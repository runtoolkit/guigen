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
guigenmc ui                  # http://127.0.0.1:8765 (default, localhost only)
guigenmc ui -p 9000          # custom port
guigenmc ui --host 0.0.0.0   # Codespaces / remote access — see security note
guigenmc ui --no-open        # don't open browser
```

Default bind address is **127.0.0.1** (localhost only).

In Codespaces: use `--host 0.0.0.0` and open the forwarded port in the browser.
When binding to all interfaces, guigenmc prints a clear warning: the API has **no authentication**.
Only use `--host 0.0.0.0` in trusted or isolated environments (port-forwarded Codespaces, local containers, etc.).

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
| `link` | Clickable external URL (tellraw `open_url`) |
| `cycle` | Cycle through options (score-based selector) |

Also supports: cost, cooldown, conditions (`item_count_*`, `score`, `has_tag`, `gamemode`, **`has_advancement`**), sounds, multi-page menus, hopper/chest minecart containers.

### New widget examples

**Link**

```json
{
  "kind": "link",
  "slot": 11,
  "item": "minecraft:writable_book",
  "name": { "text": "Discord", "color": "aqua" },
  "url": "https://discord.gg/example",
  "link_text": { "text": "Join our Discord", "color": "aqua" }
}
```

**Cycle**

```json
{
  "kind": "cycle",
  "slot": 13,
  "cycle": {
    "score": "difficulty",
    "options": [
      { "item": "minecraft:wooden_sword", "name": { "text": "Easy", "color": "green" } },
      { "item": "minecraft:iron_sword", "name": { "text": "Normal", "color": "yellow" } },
      { "item": "minecraft:diamond_sword", "name": { "text": "Hard", "color": "red" } }
    ]
  }
}
```

**has_advancement condition**

```json
{
  "kind": "button",
  "slot": 15,
  "item": "minecraft:nether_star",
  "name": { "text": "Claim Reward" },
  "commands": ["give @s minecraft:diamond 5"],
  "condition": {
    "type": "has_advancement",
    "advancement": "minecraft:story/mine_diamond",
    "fail_message": { "text": "You need the Mine Diamond advancement!", "color": "red" }
  }
}
```

---


---

## Security model

guigenmc is a **datapack generator**, not a sandbox for Minecraft commands.

| What guigenmc does | What it does **not** do |
|--------------------|-------------------------|
| Reads a JSON config and writes `.mcfunction` / datapack files | Run arbitrary OS shell commands |
| Embeds `commands` / `functions` / `on_open` / `on_close` / `tick_while_on` from your config into the generated datapack | Sandbox or filter Minecraft commands inside the config |
| Validates `namespace`, `menu_id`, and `action_id` against Minecraft resource-location rules | Protect a multiplayer server from malicious datapack content |

**Implications:**

- Config values such as `commands`, `functions`, `on_open`, `on_close`, and `tick_while_on` are copied into the generated datapack as-is. Anyone who loads that datapack can execute those Minecraft commands.
- guigenmc itself does **not** execute OS commands from the config.
- Path traversal via `namespace` / `menu_id` / `action_id` is rejected (identifiers must match `[a-z0-9._-]+`). Generated files and ZIP entries are checked so they cannot escape the output directory.
- The web UI API (`/api/generate`, `/api/validate`, `/api/zip`) has **no authentication**. Default listen address is localhost. Request bodies are limited to ~2 MiB.
- The UI ships a **bundled** copy of JSZip (`static/jszip.min.js`) so it works offline; there is no CDN dependency at runtime.

**Identifiers:** `namespace`, `menu_id`, and `action_id` must be non-empty lowercase Minecraft resource-location segments (`a-z`, `0-9`, `_`, `-`, `.`). Values containing `/`, `\`, `..`, NULL bytes, absolute paths, or Windows drive letters are rejected with a clear error (e.g. `Invalid action_id: contains path separator`).

---

## Requirements

- Python **3.9+**
- Nothing else (stdlib only)

---


---

## Install from PyPI

```bash
pip install guigenmc
guigenmc ui
```

## Publish (maintainers)

1. Create a GitHub release (tag `v1.0.0`, etc.) — or run the **Publish to PyPI** workflow manually.
2. On PyPI, add a **Trusted Publisher** for this repo:
   - Owner: your GitHub user/org  
   - Repository: `guigenmc`  
   - Workflow: `publish.yml`  
   - Environment: `pypi`
3. No API token needed (OIDC).

Local build check:

```bash
pip install build twine
python -m build
twine check dist/*
# optional TestPyPI:
# twine upload --repository testpypi dist/*
```

## License

MIT
