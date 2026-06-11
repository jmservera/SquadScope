"""Tests for scripts/manage_image_registry.py."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import scripts.manage_image_registry as registry_mod


def _tmp_registry(tmp_path: Path, images: list | None = None) -> Path:
    """Create a temporary registry file."""
    reg_path = tmp_path / "image-registry.json"
    reg_path.write_text(json.dumps({"images": images or []}, indent=2), encoding="utf-8")
    return reg_path


def _run_with_registry(tmp_path: Path, images: list | None, argv: list[str]) -> int:
    """Run the CLI with a patched REGISTRY_PATH via monkeypatching load/save defaults."""
    reg_path = _tmp_registry(tmp_path, images)
    # Patch load_registry and save_registry to use our temp path
    orig_load = registry_mod.load_registry
    orig_save = registry_mod.save_registry

    def patched_load(path: Path = reg_path, **kwargs) -> dict:
        return orig_load(path, **kwargs)

    def patched_save(registry: dict, path: Path = reg_path) -> None:
        return orig_save(registry, path)

    with patch.object(registry_mod, "load_registry", patched_load), \
         patch.object(registry_mod, "save_registry", patched_save):
        return registry_mod.main(argv)


class TestPathSafety:
    def test_rejects_http_url(self) -> None:
        safe, reason = registry_mod._is_safe_local_path("https://evil.com/img.png")
        assert not safe
        assert "URL" in reason

    def test_rejects_protocol_relative_url(self) -> None:
        safe, reason = registry_mod._is_safe_local_path("//evil.com/img.png")
        assert not safe
        assert "URL" in reason

    def test_rejects_absolute_path(self) -> None:
        safe, reason = registry_mod._is_safe_local_path("/etc/passwd")
        assert not safe
        assert "absolute" in reason

    def test_rejects_path_traversal(self) -> None:
        safe, reason = registry_mod._is_safe_local_path("assets/../../../etc/passwd")
        assert not safe
        assert "traversal" in reason

    def test_accepts_relative_path(self) -> None:
        safe, reason = registry_mod._is_safe_local_path("assets/covers/2026-W24.webp")
        assert safe
        assert reason == ""


class TestAddCommand:
    def test_rejects_url_filename(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [], [
            "add",
            "--filename", "https://example.com/image.png",
            "--license", "CC0",
            "--added-by", "test",
        ])
        assert rc == 1

    def test_rejects_traversal_filename(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [], [
            "add",
            "--filename", "assets/../../etc/shadow",
            "--license", "CC0",
            "--added-by", "test",
        ])
        assert rc == 1

    def test_adds_valid_image(self, tmp_path: Path) -> None:
        # Create a relative-path image file
        img_rel = "assets/covers/test.webp"
        img_abs = tmp_path / img_rel
        img_abs.parent.mkdir(parents=True)
        img_abs.write_bytes(b"fake image")
        # Run from tmp_path so relative path resolves
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            rc = _run_with_registry(tmp_path, [], [
                "add",
                "--filename", img_rel,
                "--license", "CC0",
                "--added-by", "test",
                "--source-url", "https://example.com/source",
                "--attribution", "Test Author",
            ])
        finally:
            os.chdir(old_cwd)
        assert rc == 0
        reg_path = tmp_path / "image-registry.json"
        data = json.loads(reg_path.read_text())
        assert len(data["images"]) == 1
        assert data["images"][0]["license"] == "CC0"
        assert data["images"][0]["source_url"] == "https://example.com/source"

    def test_rejects_duplicate(self, tmp_path: Path) -> None:
        rc = _run_with_registry(
            tmp_path,
            [{"filename": "assets/x.webp", "license": "CC0", "added_by": "op"}],
            ["add", "--filename", "assets/x.webp", "--license", "CC0", "--added-by", "test"],
        )
        assert rc == 1


class TestValidateCommand:
    def test_valid_registry_passes(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "assets/covers/img.webp", "license": "CC0", "added_by": "op"},
        ], ["validate"])
        assert rc == 0

    def test_detects_url_filename(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "https://evil.com/x.png", "license": "CC0", "added_by": "op"},
        ], ["validate"])
        assert rc == 1

    def test_detects_absolute_path(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "/etc/passwd", "license": "CC0", "added_by": "op"},
        ], ["validate"])
        assert rc == 1

    def test_detects_traversal_path(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "assets/../../../etc/shadow", "license": "CC0", "added_by": "op"},
        ], ["validate"])
        assert rc == 1

    def test_detects_missing_license(self, tmp_path: Path) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "assets/x.webp", "added_by": "op"},
        ], ["validate"])
        assert rc == 1


class TestRegistryLoading:
    def test_load_registry_rejects_invalid_json(self, tmp_path: Path) -> None:
        reg_path = tmp_path / "image-registry.json"
        reg_path.write_text("{not-json", encoding="utf-8")

        try:
            registry_mod.load_registry(reg_path)
        except registry_mod.RegistryError as exc:
            assert "Invalid image registry JSON" in str(exc)
        else:
            raise AssertionError("Expected RegistryError for invalid JSON")

    def test_load_registry_rejects_non_list_images_shape(self, tmp_path: Path) -> None:
        reg_path = tmp_path / "image-registry.json"
        reg_path.write_text(json.dumps({"images": {}}), encoding="utf-8")

        try:
            registry_mod.load_registry(reg_path)
        except registry_mod.RegistryError as exc:
            assert "expected an object with an 'images' list" in str(exc)
        else:
            raise AssertionError("Expected RegistryError for invalid registry shape")

    def test_main_reports_registry_load_errors_cleanly(self, tmp_path: Path, capsys) -> None:
        reg_path = tmp_path / "image-registry.json"
        reg_path.write_text("{not-json", encoding="utf-8")
        orig_load = registry_mod.load_registry

        def patched_load(path: Path = reg_path) -> dict:
            return orig_load(path)

        with patch.object(registry_mod, "load_registry", patched_load):
            rc = registry_mod.main(["list"])

        captured = capsys.readouterr()
        assert rc == 1
        assert "ERROR: Invalid image registry JSON" in captured.err


class TestListCommand:
    def test_lists_registered_images(self, tmp_path: Path, capsys) -> None:
        rc = _run_with_registry(tmp_path, [
            {"filename": "assets/covers/img.webp", "license": "CC0", "added_by": "op"},
        ], ["list"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "assets/covers/img.webp" in captured.out
        assert "[CC0]" in captured.out
        assert "by op" in captured.out
