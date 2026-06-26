"""Tests for the site header brand mark."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_header_brand_uses_claracle_image_asset() -> None:
    """Header brand mark must render the Claracle image through Hugo resources."""
    header = (REPO_ROOT / "layouts" / "partials" / "header.html").read_text(encoding="utf-8")
    assert 'resources.Get "images/claracle.jpeg"' in header
    assert '<img src="{{ .RelPermalink }}" width="32" height="32" alt="">' in header
    assert (
        "<svg" not in header.split('<span class="site-brand__text">Claracle</span>', maxsplit=1)[0]
    )


def test_claracle_brand_image_exists() -> None:
    """Brand image asset must exist at the path used by the header template."""
    assert (REPO_ROOT / "assets" / "images" / "claracle.jpeg").is_file()
