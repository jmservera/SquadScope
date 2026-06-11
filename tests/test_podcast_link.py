"""Tests for the configurable external podcast link feature."""

from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_podcast_url_param_exists_in_hugo_config() -> None:
    """hugo.toml must define podcast_url param (can be empty)."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    assert "podcast_url" in config


def test_footer_conditionally_renders_podcast_link() -> None:
    """Footer template must conditionally render podcast link from site param."""
    footer = (REPO_ROOT / "layouts" / "partials" / "footer.html").read_text(encoding="utf-8")
    # Must use Hugo's `with` or `if` to conditionally render
    assert "site.Params.podcast_url" in footer
    # Must pipe through safeURL to prevent unsafe schemes
    assert "safeURL" in footer
    podcast_link_match = re.search(r'<a\s+href="{{\s*site\.Params\.podcast_url\s*\|\s*trim\s*\|\s*safeURL\s*}}"\s+([^>]*)>Podcast</a>', footer)
    assert podcast_link_match, "Footer must contain a Podcast link with a sanitized podcast_url href"
    podcast_link = podcast_link_match.group(1)
    assert 'target="_blank"' in podcast_link
    assert 'rel="noopener noreferrer"' in podcast_link


def test_podcast_url_defaults_to_empty() -> None:
    """When podcast_url is empty, no link should render (Hugo `with` handles this)."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    # The default value must be empty string
    assert 'podcast_url = ""' in config
