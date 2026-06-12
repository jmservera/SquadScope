"""Tests for the configurable external podcast link feature."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_podcast_url_param_exists_in_hugo_config() -> None:
    """hugo.toml must define podcast_url param (can be empty)."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    assert "podcast_url" in config


def test_footer_conditionally_renders_podcast_link() -> None:
    """Footer template must conditionally render podcast link from site param."""
    footer = (REPO_ROOT / "layouts" / "partials" / "footer.html").read_text(encoding="utf-8")
    # Must trim before `with` so whitespace-only values are treated as falsy
    assert "site.Params.podcast_url | strings.TrimSpace" in footer
    # safeURL marks the value as trusted (bypasses scheme filtering) — safe here
    # because the value comes from controlled site config, not user input.
    assert "safeURL" in footer
    # Verify the podcast link uses dot context with correct attrs
    assert re.search(
        r'<a\s+href="{{\s*\.\s*\|\s*safeURL\s*}}"[^>]*target="_blank"[^>]*rel="noopener noreferrer"[^>]*>Podcast</a>',
        footer,
    ), "Footer podcast link must use dot context piped through safeURL with target=_blank and rel=noopener noreferrer"


def test_podcast_url_defaults_to_empty() -> None:
    """When podcast_url is empty, no link should render (Hugo `with` handles this)."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    # The default value must be empty string
    assert 'podcast_url = ""' in config
