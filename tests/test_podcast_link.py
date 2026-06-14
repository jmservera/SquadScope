"""Tests for the configurable external podcast link feature."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_podcast_url_param_exists_in_hugo_config() -> None:
    """hugo.toml must define the live Spotify podcast URL."""
    config = (REPO_ROOT / "hugo.toml").read_text(encoding="utf-8")
    assert "podcast_url" in config
    assert 'podcast_url = "https://open.spotify.com/show/033xdn5nDMoCWxB3bss2dB"' in config


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


def test_report_shortcuts_link_weekly_reports_to_spotify() -> None:
    """Weekly report shortcuts must expose the configured Spotify URL."""
    shortcuts = (REPO_ROOT / "layouts" / "partials" / "report-shortcuts.html").read_text(encoding="utf-8")
    assert 'site.Params.podcast_url | default "" | strings.TrimSpace' in shortcuts
    assert "if and $isWeekly $podcastURL" in shortcuts
    assert re.search(
        r'<a\s+href="{{\s*\$podcastURL\s*\|\s*safeURL\s*}}"[^>]*target="_blank"[^>]*rel="noopener noreferrer"[^>]*>Spotify</a>',
        shortcuts,
    ), "Weekly shortcuts must link to Spotify with target=_blank and rel=noopener noreferrer"


def test_header_exposes_spotify_button_when_podcast_url_is_configured() -> None:
    """Header actions must expose the configured Spotify URL."""
    header = (REPO_ROOT / "layouts" / "partials" / "header.html").read_text(encoding="utf-8")
    assert 'site.Params.podcast_url | default "" | strings.TrimSpace' in header
    assert 'class="icon-button spotify-button"' in header
    assert re.search(
        r'<a\s+class="icon-button spotify-button"\s+href="{{\s*\.\s*\|\s*safeURL\s*}}"[^>]*target="_blank"[^>]*rel="noopener noreferrer"[^>]*aria-label="Spotify"',
        header,
    ), "Header Spotify button must use configured URL with target=_blank and rel=noopener noreferrer"


def test_podcast_link_disabled_when_empty() -> None:
    """Templates must guard against empty/whitespace podcast_url (disabled state)."""
    footer = (REPO_ROOT / "layouts" / "partials" / "footer.html").read_text(encoding="utf-8")
    header = (REPO_ROOT / "layouts" / "partials" / "header.html").read_text(encoding="utf-8")
    # Both must use TrimSpace so whitespace-only values are treated as falsy
    assert "TrimSpace" in footer, "Footer must trim podcast_url before conditional"
    assert "TrimSpace" in header, "Header must trim podcast_url before conditional"
    # Both must use conditional (with/if) to avoid rendering empty links
    assert "with" in footer.lower() or "if" in footer.lower()
    assert "with" in header.lower() or "if" in header.lower()


def test_no_audio_hosting_or_player_pages() -> None:
    """SquadScope must not host audio, embed players, or serve podcast RSS."""
    layouts_dir = REPO_ROOT / "layouts"
    # No podcast RSS template
    for f in layouts_dir.rglob("*.xml"):
        content = f.read_text(encoding="utf-8")
        assert "<enclosure" not in content, f"{f.name} must not contain podcast RSS enclosure tags"
    # No audio player templates
    for f in layouts_dir.rglob("*.html"):
        content = f.read_text(encoding="utf-8")
        assert "<audio" not in content, f"{f.name} must not contain audio player elements"
