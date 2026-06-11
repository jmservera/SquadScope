"""Tests for scripts/validate_content_images.py."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.validate_content_images as validator


def _write_md(tmp_path: Path, filename: str, content: str) -> Path:
    """Write a markdown file in a temp content dir."""
    content_dir = tmp_path / "content"
    content_dir.mkdir(exist_ok=True)
    filepath = content_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return content_dir


class TestFrontmatterExtraction:
    def test_extracts_cover_image(self) -> None:
        text = '---\ntitle: "Test"\ncover_image: "covers/test.webp"\n---\nBody'
        fields = validator._extract_frontmatter(text)
        assert fields["cover_image"] == "covers/test.webp"

    def test_extracts_og_image(self) -> None:
        text = '---\nog_image: "covers/og.png"\n---\n'
        fields = validator._extract_frontmatter(text)
        assert fields["og_image"] == "covers/og.png"

    def test_ignores_non_image_fields(self) -> None:
        text = '---\ntitle: "Hello"\nauthor: "Test"\n---\n'
        fields = validator._extract_frontmatter(text)
        assert fields == {}

    def test_handles_no_frontmatter(self) -> None:
        text = "Just some content"
        fields = validator._extract_frontmatter(text)
        assert fields == {}


class TestHotlinkDetection:
    def test_detects_frontmatter_hotlink(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "https://evil.com/img.png"\n---\nBody',
        )
        violations = validator.validate_content(content_dir)
        assert any("hotlinks external URL" in v for v in violations)

    def test_detects_markdown_image_hotlink(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            "---\ntitle: test\n---\n![alt](https://example.com/photo.jpg)\n",
        )
        violations = validator.validate_content(content_dir)
        assert any("Markdown image hotlinks" in v for v in violations)

    def test_detects_html_img_hotlink(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ntitle: test\n---\n<img src="http://evil.com/x.png" alt="bad">\n',
        )
        violations = validator.validate_content(content_dir)
        assert any("HTML img hotlinks" in v for v in violations)

    def test_detects_protocol_relative_url(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\nog_image: "//cdn.example.com/image.png"\n---\n',
        )
        violations = validator.validate_content(content_dir)
        assert any("hotlinks external URL" in v for v in violations)

    def test_allows_local_paths(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "covers/local.webp"\n---\n![alt](/images/chart.svg)\n',
        )
        violations = validator.validate_content(content_dir)
        assert len(violations) == 0


class TestSecretDetection:
    def test_detects_sas_token(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            "---\ntitle: test\n---\n![x](https://store.blob.core.windows.net/c/img.png?sv=2021&sig=abc)\n",
        )
        violations = validator.validate_content(content_dir)
        assert any("suspicious parameters" in v for v in violations)

    def test_detects_tracking_params(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            "---\ntitle: test\n---\n![x](https://example.com/img.png?utm_source=twitter&utm_medium=social)\n",
        )
        violations = validator.validate_content(content_dir)
        assert any("suspicious parameters" in v for v in violations)

    def test_detects_api_key_param(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "covers/x.webp?api_key=secret123"\n---\n',
        )
        violations = validator.validate_content(content_dir)
        assert any("suspicious parameters" in v for v in violations)


class TestRegistryValidation:
    def test_flags_unregistered_cover(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "covers/unregistered.webp"\n---\nBody',
        )
        reg_path = tmp_path / "registry.json"
        reg_path.write_text(json.dumps({"images": []}), encoding="utf-8")
        violations = validator.validate_registry_references(content_dir, reg_path)
        assert any("unregistered image" in v for v in violations)

    def test_passes_registered_cover(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "covers/registered.webp"\n---\nBody',
        )
        reg_path = tmp_path / "registry.json"
        reg_path.write_text(
            json.dumps({"images": [{"filename": "covers/registered.webp", "license": "CC0", "added_by": "test"}]}),
            encoding="utf-8",
        )
        violations = validator.validate_registry_references(content_dir, reg_path)
        assert len(violations) == 0

    def test_ignores_non_cover_local_paths(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "images/generated-chart.svg"\n---\nBody',
        )
        reg_path = tmp_path / "registry.json"
        reg_path.write_text(json.dumps({"images": []}), encoding="utf-8")
        violations = validator.validate_registry_references(content_dir, reg_path)
        # Non-cover paths (not starting with covers/ or assets/covers/) are not flagged
        assert len(violations) == 0

    def test_handles_missing_registry(self, tmp_path: Path) -> None:
        content_dir = _write_md(
            tmp_path, "test.md",
            '---\ncover_image: "covers/x.webp"\n---\n',
        )
        violations = validator.validate_registry_references(content_dir, tmp_path / "nonexistent.json")
        assert len(violations) == 1
        assert "not found" in violations[0]


class TestHelpers:
    def test_is_remote_url_http(self) -> None:
        assert validator._is_remote_url("http://example.com/img.png")

    def test_is_remote_url_https(self) -> None:
        assert validator._is_remote_url("https://example.com/img.png")

    def test_is_remote_url_protocol_relative(self) -> None:
        assert validator._is_remote_url("//cdn.example.com/img.png")

    def test_is_not_remote_url_local(self) -> None:
        assert not validator._is_remote_url("covers/local.webp")

    def test_is_not_remote_url_relative(self) -> None:
        assert not validator._is_remote_url("assets/images/chart.svg")
