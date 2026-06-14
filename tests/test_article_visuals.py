from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIS = ROOT / "layouts/partials/visuals"
SC = ROOT / "layouts/shortcodes"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_visual_module_partials_exist() -> None:
    for name in (
        "article-cover.html",
        "cover-card.html",
        "topic-constellation.html",
        "signal-noise.html",
        "repo-trend.html",
        "fallback-card.html",
    ):
        assert (VIS / name).is_file(), f"missing visual partial {name}"


def test_reusable_shortcodes_exist() -> None:
    for name in ("signal-noise.html", "topic-stars.html", "repo-trend.html"):
        assert (SC / name).is_file(), f"missing shortcode {name}"


def test_weekly_single_wires_cover_and_signal_noise() -> None:
    single = _read(ROOT / "layouts/weekly/single.html")
    assert 'partial "visuals/article-cover.html"' in single
    assert 'partial "visuals/signal-noise.html"' in single


def test_generated_visuals_have_accessible_names() -> None:
    cover = _read(VIS / "cover-card.html")
    # The figure must NOT use role="img": that collapses the whole container into a
    # single image node and hides its real text (kicker, brand, topics) from AT.
    assert 'role="img"' not in cover
    # It still exposes a real-data accessible name, keeps the topic text in the DOM
    # (not aria-hidden), and hides only the decorative motif.
    assert "aria-label=" in cover
    assert 'aria-hidden="true"' in cover
    assert 'class="article-cover__topics"' in cover  # real topic text stays exposed
    trend = _read(VIS / "repo-trend.html")
    assert "visually-hidden" in trend  # text summary for the chart data
    assert 'aria-hidden="true"' in trend


def test_visuals_are_locally_generated_not_hotlinked() -> None:
    # No external/hotlinked image sources in any visual partial.
    for p in VIS.glob("*.html"):
        text = _read(p)
        assert "http://" not in text, f"{p.name} must not hotlink http assets"
        # GitHub repo deep-links are allowed as anchors, but never as <img src>.
        for marker in ("img src=\"http", "src='http"):
            assert marker not in text.replace(" ", ""), f"{p.name} hotlinks an image"


def test_safe_cover_only_accepts_local_resources() -> None:
    orch = _read(VIS / "article-cover.html")
    # Image path resolves Hugo resources (local hosting), matched exactly and
    # guarded to image types, before rendering an <img>.
    assert "Resources.GetMatch" in orch
    assert "resources.Get" in orch
    assert 'eq $candidate.ResourceType "image"' in orch
    assert "#329" in orch  # documented image-policy hook


def test_heading_levels_are_whitelisted() -> None:
    # Untrusted `level` (shortcode/frontmatter) must be normalized + whitelisted
    # before being used as a raw HTML tag name.
    for name in ("topic-constellation.html", "signal-noise.html", "repo-trend.html"):
        text = _read(VIS / name)
        assert '| lower' in text
        assert 'in (slice "h2" "h3" "h4" "h5" "h6")' in text
        # The tag name is emitted only from the whitelisted value via safeHTML,
        # never by interpolating the raw input as a tag name (`<{{ $level }}>`).
        assert "<{{ $level }}>" not in text
        assert "| safeHTML" in text


def test_topic_constellation_coerces_numeric_figures() -> None:
    # `.repos`/`.stars` arrive as strings from the shortcode (`.Get`); only
    # digit strings are passed to lang.FormatNumber, non-numeric input is dropped
    # rather than erroring the build.
    text = _read(VIS / "topic-constellation.html")
    assert 'findRE "^[0-9]+$"' in text
    assert "lang.FormatNumber 0 (int" in text


def test_topic_titles_are_non_interactive_labels() -> None:
    # Operator ask (#328): topic titles must NOT look (or be) clickable. They are
    # rendered as plain labels — no link, no button/pill affordance — while the
    # chart itself stays intact.
    cover = _read(VIS / "cover-card.html")
    constellation = _read(VIS / "topic-constellation.html")
    # No anchors around topic chips in either module.
    assert "<a href=" not in cover, "cover topic chips must not be links"
    assert "<a href=" not in constellation, "constellation chips must not be links"
    # The topic list/text is still present (chart intact).
    assert 'class="article-cover__topics"' in cover
    assert 'class="article-cover__topic"' in cover
    # CSS must not give the chips a button/pill affordance (background/border/hover).
    css = _read(ROOT / "assets/css/extended/article-visuals.css")
    for sel in (
        ".article-cover__topic--link",
        ".article-cover__topic--static",
        ".topic-stars__chip--link",
        ".topic-stars__chip--static",
    ):
        assert sel not in css, f"stale clickable-chip rule remains: {sel}"


def test_unsafe_markdown_remains_disabled() -> None:
    cfg = _read(ROOT / "hugo.toml")
    assert "unsafe = false" in cfg


def test_visuals_keep_claracle_brand() -> None:
    cover = _read(VIS / "cover-card.html")
    assert "Claracle" in cover
    # Do not reintroduce the retired display brand in visible text.
    for p in VIS.glob("*.html"):
        assert "SquadScope" not in _read(p)


def test_signal_noise_module_preserves_caveat_slot() -> None:
    sn = _read(VIS / "signal-noise.html")
    assert "signal-noise__caveat" in sn  # evidence-first: caveat language supported
    assert "signal-noise__source" in sn


def test_article_visuals_css_is_responsive() -> None:
    css = _read(ROOT / "assets/css/extended/article-visuals.css")
    assert "@media (max-width: 768px)" in css
    assert "aspect-ratio" in css  # reserve space -> no CLS


# -----------------------------------------------------------------------
# Cover image pipeline validation (issue #358 acceptance criteria)
# -----------------------------------------------------------------------


def test_og_image_template_uses_1200x630() -> None:
    """OG image must be resized to 1200x630 per issue #358 criterion 3."""
    og = _read(ROOT / "layouts/partials/templates/opengraph.html")
    assert "1200x630" in og, "OG template must resize to 1200x630"


def test_cover_card_uses_800x400_with_srcset() -> None:
    """Cover card must use 800x400 base with responsive srcset per issue #358 criterion 3."""
    cover = _read(VIS / "article-cover.html")
    assert "800x400" in cover, "Cover card must produce 800x400 base size"
    assert "1600x800" in cover, "Cover card must produce 1600x800 for 2x srcset"
    assert "srcset" in cover, "Cover card must use responsive srcset"


def test_cover_only_renders_local_resources() -> None:
    """Cover template must only render locally-hosted images (no hotlinking)."""
    cover = _read(VIS / "article-cover.html")
    assert "Resources.GetMatch" in cover or "resources.Get" in cover
    assert "hotlink" in cover.lower() or "locally-hosted" in cover.lower()


def test_image_registry_exists_with_required_fields() -> None:
    """data/image-registry.json must exist with required schema fields."""
    import json
    registry_path = ROOT / "data" / "image-registry.json"
    assert registry_path.exists(), "Image registry must exist at data/image-registry.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    assert isinstance(data, (dict, list)), "Image registry must be JSON object or array"
