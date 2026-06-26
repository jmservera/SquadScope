"""Tests for site icon metadata."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_head_favicons_use_claracle_image_asset() -> None:
    """Head template must derive browser icons from the Claracle image asset."""
    head = (REPO_ROOT / "layouts" / "partials" / "head.html").read_text(encoding="utf-8")
    assert 'resources.Get "images/claracle.jpeg"' in head
    assert '.Fill "16x16 png"' in head
    assert '.Fill "32x32 png"' in head
    assert '.Fill "180x180 png"' in head
    assert "/images/squadscope-icon.svg" not in head
    assert "/favicon-16x16.png" not in head
    assert "/favicon-32x32.png" not in head
    assert "/apple-touch-icon.png" not in head


def test_web_manifest_uses_claracle_image_icon() -> None:
    """Web app manifest must point at compatible PNG site icons."""
    manifest = json.loads((REPO_ROOT / "static" / "site.webmanifest").read_text(encoding="utf-8"))
    icons = manifest["icons"]
    assert icons == [
        {"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
        {
            "src": "/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable",
        },
    ]


def test_static_icon_png_files_exist() -> None:
    """All browser and app icon files must exist as PNG files."""
    for icon_path in (
        "favicon-16x16.png",
        "favicon-32x32.png",
        "apple-touch-icon.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
    ):
        icon = REPO_ROOT / "static" / icon_path
        assert icon.is_file()
        assert icon.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
