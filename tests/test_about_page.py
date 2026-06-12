"""Tests for About page content."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_about_page_includes_claracle_image() -> None:
    """About page should link the full Claracle image to Spotify near the top."""
    about = (REPO_ROOT / "content" / "about" / "_index.md").read_text(encoding="utf-8")
    linked_image = "[![Claracle visual identity](/images/claracle.jpeg)](https://open.spotify.com/show/033xdn5nDMoCWxB3bss2dB)"
    assert linked_image in about
    assert about.index(linked_image) < about.index("Claracle surfaces")