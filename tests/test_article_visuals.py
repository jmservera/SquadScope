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
