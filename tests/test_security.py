"""Security regression tests for path traversal, identifiers, and HTTP limits."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from guigenmc.cli import MAX_REQUEST_BODY_BYTES, GuigenHandler
from guigenmc.generators import generate_datapack
from guigenmc.models import load_menu_from_json_string, menu_from_dict
from guigenmc.security import (
    MAX_GENERATED_FILES,
    MAX_JSON_DEPTH,
    assert_generated_paths_safe,
    assert_generated_size_limits,
    check_json_structure,
    check_no_symlink_escape,
    ensure_within_output_root,
    is_safe_relative_path,
    safe_write_text,
    validate_identifier,
    validate_zip_entry_name,
)


def _minimal_config(**overrides):
    cfg = {
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
                        "name": {"text": "Get Diamond", "color": "aqua"},
                        "commands": ["give @s minecraft:diamond 1"],
                    },
                    {"kind": "close", "slot": 26},
                ],
            }
        ],
    }
    cfg.update(overrides)
    return cfg


class TestIdentifierValidation(unittest.TestCase):
    def test_normal_namespace(self):
        self.assertEqual(validate_identifier("mymod", "namespace"), "mymod")
        self.assertEqual(validate_identifier("my_mod", "namespace"), "my_mod")
        self.assertEqual(validate_identifier("my.mod-1", "namespace"), "my.mod-1")

    def test_invalid_namespace(self):
        with self.assertRaises(ValueError) as cm:
            validate_identifier("MyMod", "namespace")
        self.assertIn("namespace", str(cm.exception))

        with self.assertRaises(ValueError):
            validate_identifier("", "namespace")

        with self.assertRaises(ValueError):
            validate_identifier("has space", "namespace")

    def test_parent_directory_traversal(self):
        with self.assertRaises(ValueError) as cm:
            validate_identifier("..", "namespace")
        msg = str(cm.exception).lower()
        self.assertTrue(
            "parent" in msg or "path" in msg or "invalid" in msg,
            f"unexpected message: {cm.exception}",
        )

        with self.assertRaises(ValueError):
            menu_from_dict(_minimal_config(namespace="../evil"))

    def test_nested_parent_traversal(self):
        with self.assertRaises(ValueError):
            menu_from_dict(_minimal_config(namespace="foo/../../bar"))

        with self.assertRaises(ValueError):
            menu_from_dict(_minimal_config(menu_id="a/../b"))

    def test_absolute_path(self):
        with self.assertRaises(ValueError):
            menu_from_dict(_minimal_config(namespace="/etc/passwd"))

        with self.assertRaises(ValueError):
            validate_identifier("/abs", "namespace")

    def test_windows_style_path(self):
        with self.assertRaises(ValueError):
            menu_from_dict(_minimal_config(menu_id="C:evil"))

        # drive letter forms rejected by path helpers
        self.assertFalse(is_safe_relative_path(r"C:\evil"))
        self.assertFalse(is_safe_relative_path("C:/evil"))

    def test_backslash_traversal(self):
        with self.assertRaises(ValueError):
            validate_identifier("foo\\bar", "action_id")
        self.assertFalse(is_safe_relative_path(r"..\evil"))
        self.assertFalse(is_safe_relative_path(r"foo\..\bar"))

    def test_action_id_traversal(self):
        cfg = _minimal_config()
        cfg["pages"][0]["widgets"][0]["action_id"] = "../evil"
        with self.assertRaises(ValueError) as cm:
            menu_from_dict(cfg)
        self.assertIn("action_id", str(cm.exception))

        cfg2 = _minimal_config()
        cfg2["pages"][0]["widgets"][0]["action_id"] = "ok_id"
        menu = menu_from_dict(cfg2)
        self.assertEqual(menu["pages"][0]["widgets"][0]["action_id"], "ok_id")

    def test_menu_id_traversal(self):
        with self.assertRaises(ValueError) as cm:
            menu_from_dict(_minimal_config(menu_id="../../tmp"))
        self.assertIn("menu_id", str(cm.exception))

    def test_null_byte(self):
        with self.assertRaises(ValueError):
            validate_identifier("foo\x00bar", "namespace")
        self.assertFalse(is_safe_relative_path("foo\x00bar"))


class TestPathSafety(unittest.TestCase):
    def test_is_safe_relative_path(self):
        self.assertTrue(is_safe_relative_path("data/mymod/function/core/load.mcfunction"))
        self.assertTrue(is_safe_relative_path("pack.mcmeta"))
        self.assertFalse(is_safe_relative_path("../evil"))
        self.assertFalse(is_safe_relative_path("foo/../../bar"))
        self.assertFalse(is_safe_relative_path("/absolute/path"))
        self.assertFalse(is_safe_relative_path(""))
        self.assertFalse(is_safe_relative_path("."))
        # PurePosixPath collapses "a/./b" → "a/b"; reject explicit ".." instead
        self.assertFalse(is_safe_relative_path("a/../b"))
        self.assertFalse(is_safe_relative_path("a/.."))

    def test_ensure_within_output_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = ensure_within_output_root(root, "data/ns/function/x.mcfunction")
            self.assertTrue(str(good).startswith(str(root.resolve())))

            with self.assertRaises(ValueError):
                ensure_within_output_root(root, "../outside")

            with self.assertRaises(ValueError):
                ensure_within_output_root(root, "/etc/passwd")

    def test_zip_path_traversal(self):
        with self.assertRaises(ValueError):
            validate_zip_entry_name("../evil.mcfunction")
        with self.assertRaises(ValueError):
            validate_zip_entry_name("/absolute/path")
        with self.assertRaises(ValueError):
            validate_zip_entry_name(r"C:\evil")
        validate_zip_entry_name("data/mymod/function/core/load.mcfunction")

    def test_generated_files_stay_inside_output_root(self):
        menu = menu_from_dict(_minimal_config())
        files = generate_datapack(menu)
        assert_generated_paths_safe(files)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "pack"
            out_dir.mkdir()
            for rel, content in files.items():
                dest = ensure_within_output_root(out_dir, rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
                # resolved path must be under out_dir
                self.assertTrue(
                    out_dir.resolve() in dest.resolve().parents
                    or dest.resolve() == out_dir.resolve()
                )

            # ZIP entries also safe
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                for rel, content in files.items():
                    validate_zip_entry_name(rel)
                    zf.writestr(rel, content)
            with zipfile.ZipFile(buf) as zf:
                for name in zf.namelist():
                    self.assertTrue(is_safe_relative_path(name))


class TestValidGeneration(unittest.TestCase):
    def test_normal_config_still_generates(self):
        menu = load_menu_from_json_string(json.dumps(_minimal_config()))
        files = generate_datapack(menu)
        self.assertIn("pack.mcmeta", files)
        self.assertTrue(any(p.endswith("open.mcfunction") for p in files))
        self.assertTrue(any("click/" in p for p in files))
        # namespace and menu_id appear in paths
        self.assertTrue(any("mymod" in p for p in files))
        self.assertTrue(any("shop" in p for p in files))


class TestHttpLimits(unittest.TestCase):
    def _make_handler(self):
        # Minimal fake handler without binding a real socket.
        handler = GuigenHandler.__new__(GuigenHandler)
        handler.headers = {}
        handler.rfile = io.BytesIO()
        handler.wfile = io.BytesIO()
        handler.path = "/api/validate"
        handler.responses = []

        def json_response(status, body):
            handler.responses.append((status, body))

        handler._json_response = json_response  # type: ignore[method-assign]
        return handler

    def test_request_too_large(self):
        handler = self._make_handler()
        handler.headers = {"Content-Length": str(MAX_REQUEST_BODY_BYTES + 1)}
        handler.do_POST()
        self.assertEqual(len(handler.responses), 1)
        status, body = handler.responses[0]
        self.assertEqual(status, 413)
        self.assertFalse(body.get("ok", True))

    def test_invalid_content_length(self):
        handler = self._make_handler()
        handler.headers = {"Content-Length": "not-a-number"}
        handler.do_POST()
        self.assertEqual(len(handler.responses), 1)
        status, body = handler.responses[0]
        self.assertEqual(status, 400)
        self.assertIn("Content-Length", body.get("error", ""))

    def test_missing_content_length(self):
        handler = self._make_handler()
        handler.headers = {}
        handler.do_POST()
        self.assertEqual(len(handler.responses), 1)
        status, body = handler.responses[0]
        self.assertEqual(status, 411)


class TestSymlinkSafety(unittest.TestCase):
    def test_safe_write_normal(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pack"
            out.mkdir()
            dest = safe_write_text(out, "data/ns/x.mcfunction", "say hi\n")
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_text(encoding="utf-8"), "say hi\n")
            self.assertTrue(out.resolve() in dest.resolve().parents)

    def test_refuses_symlink_file_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "pack"
            out.mkdir()
            outside = root / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            # Place a symlink inside the output tree pointing outside.
            link = out / "evil.mcfunction"
            link.symlink_to(outside)
            with self.assertRaises(ValueError) as cm:
                safe_write_text(out, "evil.mcfunction", "pwned\n")
            msg = str(cm.exception).lower()
            self.assertTrue(
                "symlink" in msg or "escapes" in msg or "outside" in msg,
                f"unexpected message: {cm.exception}",
            )
            # Outside file must remain untouched.
            self.assertEqual(outside.read_text(encoding="utf-8"), "secret")

    def test_refuses_symlink_parent_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "pack"
            out.mkdir()
            outside_dir = root / "outside_dir"
            outside_dir.mkdir()
            # data -> outside_dir
            (out / "data").symlink_to(outside_dir)
            with self.assertRaises(ValueError):
                check_no_symlink_escape(out, "data/ns/x.mcfunction")


class TestJsonStructureLimits(unittest.TestCase):
    def test_normal_json_ok(self):
        check_json_structure({"a": 1, "b": [1, 2, {"c": 3}]})

    def test_depth_rejected(self):
        obj: object = "leaf"
        for _ in range(MAX_JSON_DEPTH + 5):
            obj = [obj]
        with self.assertRaises(ValueError) as cm:
            check_json_structure(obj)
        self.assertIn("depth", str(cm.exception).lower())

    def test_load_menu_rejects_deep_json(self):
        # Build nested structure that exceeds depth but stays small in bytes.
        inner = {"kind": "close", "slot": 0}
        page = {"index": 0, "name": "P", "widgets": [inner]}
        # Nest under a deep "extra" key chain so root still has namespace/menu_id.
        deep: object = "x"
        for _ in range(MAX_JSON_DEPTH + 5):
            deep = {"n": deep}
        cfg = {
            "namespace": "mymod",
            "menu_id": "shop",
            "pages": [page],
            "extra_deep": deep,
        }
        with self.assertRaises(ValueError) as cm:
            load_menu_from_json_string(json.dumps(cfg))
        self.assertIn("depth", str(cm.exception).lower())


class TestOutputSizeLimits(unittest.TestCase):
    def test_normal_output_within_limits(self):
        menu = menu_from_dict(_minimal_config())
        files = generate_datapack(menu)
        assert_generated_size_limits(files)

    def test_too_many_files_rejected(self):
        huge = {f"f{i}.txt": "x" for i in range(MAX_GENERATED_FILES + 1)}
        with self.assertRaises(ValueError) as cm:
            assert_generated_size_limits(huge)
        self.assertIn("too many files", str(cm.exception).lower())


if __name__ == "__main__":
    unittest.main()
