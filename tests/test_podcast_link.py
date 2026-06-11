"""Tests for the configurable external podcast link feature."""

from __future__ import annotations

from pathlib import Path

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
    # Must open in new tab with noopener
    assert 'target="_blank"' in footer
    assert 'rel="noopener"' in footer
    # Must include the word "Podcast" as link text
    assert ">Podcast<" in footer


def test_podcast_url_defaults_to_empty() -> None:
    """When podcast_url is empty, no link should render (Hugo `with` handles this)."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    # The default value must be empty string
    assert 'podcast_url = ""' in config
