"""guigenmc CLI — easy, colorful, Codespaces / Linux / macOS / GitHub Actions friendly."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import webbrowser
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import __version__
from .generators import generate_datapack, summarize
from .models import load_menu_from_file, load_menu_from_json_string
from .validate import validate_menu

# ---------------------------------------------------------------------------
# Colors — pure ANSI, works everywhere (GHA, Codespaces, macOS, Linux).
# Auto-disable when not a TTY or NO_COLOR is set.
# ---------------------------------------------------------------------------

_FORCE = os.environ.get("FORCE_COLOR", "").strip() in ("1", "true", "yes")
_NO_COLOR = os.environ.get("NO_COLOR", "").strip() != ""
_IS_TTY = sys.stdout.isatty()
_USE_COLOR = _FORCE or (not _NO_COLOR and _IS_TTY)


class C:
    """ANSI color helpers. Empty strings when color is off."""

    RESET = "\033[0m" if _USE_COLOR else ""
    BOLD = "\033[1m" if _USE_COLOR else ""
    DIM = "\033[2m" if _USE_COLOR else ""
    GREEN = "\033[32m" if _USE_COLOR else ""
    YELLOW = "\033[33m" if _USE_COLOR else ""
    RED = "\033[31m" if _USE_COLOR else ""
    CYAN = "\033[36m" if _USE_COLOR else ""
    MAGENTA = "\033[35m" if _USE_COLOR else ""
    BLUE = "\033[34m" if _USE_COLOR else ""
    WHITE = "\033[37m" if _USE_COLOR else ""


def ok(msg: str) -> None:
    print(f"{C.GREEN}✓{C.RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{C.YELLOW}⚠{C.RESET} {msg}")


def err(msg: str) -> None:
    print(f"{C.RED}✗{C.RESET} {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(f"{C.CYAN}→{C.RESET} {msg}")


def header(msg: str) -> None:
    print(f"\n{C.BOLD}{C.MAGENTA}● guigenmc{C.RESET} {C.DIM}{msg}{C.RESET}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate a datapack from a JSON config."""
    config_path = Path(args.config)
    if not config_path.is_file():
        err(f"Config not found: {config_path}")
        return 1

    header(f"v{__version__}")
    info(f"Reading {C.BOLD}{config_path}{C.RESET} …")

    try:
        menu = load_menu_from_file(str(config_path))
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        err(f"Config error: {e}")
        return 1

    warnings = validate_menu(menu)
    for w in warnings:
        warn(w)

    info("Generating datapack files …")
    try:
        files = generate_datapack(menu)
    except Exception as e:
        err(f"Generation failed: {e}")
        return 1

    summary = summarize(menu)
    print()
    print(f"  {C.DIM}namespace{C.RESET}   {C.GREEN}{summary['namespace']}{C.RESET}")
    print(f"  {C.DIM}menu_id{C.RESET}     {C.GREEN}{summary['menu_id']}{C.RESET}")
    print(f"  {C.DIM}pages / widgets{C.RESET}  {summary['pages']} / {summary['widgets']}")
    print(f"  {C.DIM}container{C.RESET}   {summary['container']}")
    print(f"  {C.DIM}open with{C.RESET}   {C.CYAN}{summary['open_command']}{C.RESET}")
    print()

    out_dir = Path(args.output or f"{summary['menu_id']}_datapack")
    as_zip = args.zip or str(out_dir).endswith(".zip")

    if as_zip:
        zip_path = out_dir if str(out_dir).endswith(".zip") else Path(str(out_dir) + ".zip")
        if zip_path.exists() and not args.force:
            err(f"{zip_path} already exists. Use --force to overwrite.")
            return 1
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel, content in sorted(files.items()):
                zf.writestr(rel, content)
        ok(f"Wrote {C.BOLD}{len(files)}{C.RESET} files → {C.BOLD}{zip_path}{C.RESET}")
    else:
        if out_dir.exists():
            if not args.force:
                err(f"{out_dir} already exists. Use --force to overwrite.")
                return 1
            shutil.rmtree(out_dir)
        for rel, content in files.items():
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        ok(f"Wrote {C.BOLD}{len(files)}{C.RESET} files → {C.BOLD}{out_dir}/{C.RESET}")

    if warnings:
        warn(f"{len(warnings)} warning(s) — generated anyway, but worth checking.")
    else:
        ok("No warnings.")

    print()
    info("In Minecraft:")
    print(f"  1. Put the datapack in  {C.DIM}world/datapacks/{C.RESET}")
    print(f"  2. Run  {C.CYAN}/reload{C.RESET}")
    print(f"  3. Run  {C.CYAN}{summary['open_command']}{C.RESET}")
    print()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Check a config for errors and warnings without generating."""
    config_path = Path(args.config)
    if not config_path.is_file():
        err(f"Config not found: {config_path}")
        return 1

    header("validate")
    try:
        menu = load_menu_from_file(str(config_path))
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        err(f"Config error: {e}")
        return 1

    summary = summarize(menu)
    ok(f"Config OK — {summary['pages']} page(s), {summary['widgets']} widget(s)")
    warnings = validate_menu(menu)
    for w in warnings:
        warn(w)
    if not warnings:
        ok("No warnings.")
    return 0


def cmd_tree(args: argparse.Namespace) -> int:
    """Show the file tree that would be generated (no write)."""
    config_path = Path(args.config)
    if not config_path.is_file():
        err(f"Config not found: {config_path}")
        return 1

    try:
        menu = load_menu_from_file(str(config_path))
        files = generate_datapack(menu)
    except (json.JSONDecodeError, ValueError, TypeError, Exception) as e:
        err(str(e))
        return 1

    header("tree preview")
    for path in sorted(files):
        size = len(files[path])
        size_s = f"{size}B" if size < 1024 else f"{size / 1024:.1f}K"
        if path.endswith(".mcfunction"):
            icon = f"{C.CYAN}ƒ{C.RESET}"
        elif path.endswith(".json"):
            icon = f"{C.YELLOW}{{}}{C.RESET}"
        elif path.endswith(".mcmeta"):
            icon = f"{C.MAGENTA}◆{C.RESET}"
        else:
            icon = "·"
        print(f"  {icon} {path}  {C.DIM}{size_s}{C.RESET}")
    print()
    ok(f"{len(files)} files")
    return 0


# ---------------------------------------------------------------------------
# Web UI server (stdlib only)
# ---------------------------------------------------------------------------


def _static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"


class guigenmcHandler(SimpleHTTPRequestHandler):
    """Serve the web UI + JSON API that uses the Python generator."""

    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Quieter logs: only show path
        sys.stderr.write(f"  {C.DIM}{self.address_string()}{C.RESET}  {args[0]}\n")

    def end_headers(self) -> None:
        # Allow local UI to talk to API from same origin
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()
        if parsed.path == "/api/health":
            return self._json_response(200, {"ok": True, "version": __version__})
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"

        if parsed.path == "/api/generate":
            return self._handle_generate(raw)
        if parsed.path == "/api/validate":
            return self._handle_validate(raw)
        if parsed.path == "/api/zip":
            return self._handle_zip(raw)

        self._json_response(404, {"error": "not found"})

    def _read_config(self, raw: bytes) -> dict[str, Any]:
        data = json.loads(raw.decode("utf-8") or "{}")
        # Accept either raw menu object or { "config": {...} } / { "json": "..." }
        if isinstance(data, dict) and "config" in data:
            cfg = data["config"]
            if isinstance(cfg, str):
                return load_menu_from_json_string(cfg)
            return load_menu_from_json_string(json.dumps(cfg))
        if isinstance(data, dict) and "json" in data and isinstance(data["json"], str):
            return load_menu_from_json_string(data["json"])
        return load_menu_from_json_string(json.dumps(data))

    def _handle_generate(self, raw: bytes) -> None:
        try:
            menu = self._read_config(raw)
            files = generate_datapack(menu)
            summary = summarize(menu)
            warnings = validate_menu(menu)
            self._json_response(
                200,
                {
                    "ok": True,
                    "summary": summary,
                    "warnings": warnings,
                    "files": files,
                    "file_count": len(files),
                },
            )
        except Exception as e:
            self._json_response(400, {"ok": False, "error": str(e)})

    def _handle_validate(self, raw: bytes) -> None:
        try:
            menu = self._read_config(raw)
            summary = summarize(menu)
            warnings = validate_menu(menu)
            self._json_response(
                200,
                {"ok": True, "summary": summary, "warnings": warnings},
            )
        except Exception as e:
            self._json_response(400, {"ok": False, "error": str(e)})

    def _handle_zip(self, raw: bytes) -> None:
        try:
            menu = self._read_config(raw)
            files = generate_datapack(menu)
            menu_id = menu.get("menu_id") or "datapack"
            import io

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for rel, content in sorted(files.items()):
                    zf.writestr(rel, content)
            payload = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{menu_id}_datapack.zip"',
            )
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as e:
            self._json_response(400, {"ok": False, "error": str(e)})

    def _json_response(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def cmd_ui(args: argparse.Namespace) -> int:
    """Start the local web UI in the browser."""
    static = _static_dir()
    index = static / "index.html"
    if not index.is_file():
        err(f"UI files missing: {index}")
        return 1

    host = args.host
    port = int(args.port)
    handler = partial(guigenmcHandler, directory=str(static))

    try:
        server = ThreadingHTTPServer((host, port), handler)
    except OSError as e:
        err(f"Could not bind {host}:{port} — {e}")
        return 1

    url = f"http://127.0.0.1:{port}/" if host in ("0.0.0.0", "::") else f"http://{host}:{port}/"
    header(f"ui  v{__version__}")
    ok(f"Web UI running at  {C.BOLD}{C.CYAN}{url}{C.RESET}")
    info("Press Ctrl+C to stop.")
    print()

    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        ok("Stopped.")
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="guigenmc",
        description="JSON → Minecraft GUI datapack generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{C.BOLD}Quick start:{C.RESET}

  guigenmc ui                          # open the visual editor in your browser
  guigenmc generate my_menu.json       # build datapack from a JSON file
  guigenmc generate my_menu.json -z    # build a .zip instead

{C.DIM}Works on Linux, macOS, GitHub Codespaces & GitHub Actions.{C.RESET}
""",
    )
    p.add_argument("-v", "--version", action="version", version=f"guigenmc {__version__}")

    sub = p.add_subparsers(dest="command", metavar="COMMAND")

    # ui
    u = sub.add_parser("ui", help="Open the visual web editor in your browser")
    u.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    u.add_argument("-p", "--port", type=int, default=8765, help="Port (default: 8765)")
    u.add_argument("--no-open", action="store_true", help="Don't open the browser automatically")
    u.set_defaults(func=cmd_ui)

    # generate
    g = sub.add_parser("generate", aliases=["gen", "g"], help="Generate datapack from config")
    g.add_argument("config", help="Path to config.json")
    g.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output folder or .zip path (default: <menu_id>_datapack)",
    )
    g.add_argument("-z", "--zip", action="store_true", help="Write a .zip instead of a folder")
    g.add_argument("-f", "--force", action="store_true", help="Overwrite if exists")
    g.set_defaults(func=cmd_generate)

    # validate
    v = sub.add_parser("validate", aliases=["check"], help="Check config for errors/warnings")
    v.add_argument("config", help="Path to config.json")
    v.set_defaults(func=cmd_validate)

    # tree
    t = sub.add_parser("tree", help="Preview generated file tree (no write)")
    t.add_argument("config", help="Path to config.json")
    t.set_defaults(func=cmd_tree)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        print()
        info(f"Tip: open the editor with  {C.CYAN}guigenmc ui{C.RESET}")
        return 0

    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
