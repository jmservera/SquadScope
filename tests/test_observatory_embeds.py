from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "content/charts/embeddable-rankings/index.md"
EMBED = ROOT / "content/embeds/fastest-growing-ai-repositories-chart/index.md"


def test_chart_content_uses_shortcodes_not_raw_html() -> None:
    for path in (DEMO, EMBED):
        content = path.read_text(encoding="utf-8")
        assert "<iframe" not in content
        assert "<script" not in content
        assert "<div" not in content
    assert "{{< observatory-chart" in DEMO.read_text(encoding="utf-8")


def test_chart_shortcode_and_embed_layout_are_local_and_attributed() -> None:
    shortcode = (ROOT / "layouts/shortcodes/observatory-chart.html").read_text(encoding="utf-8")
    partial = (ROOT / "layouts/partials/visuals/observatory-chart.html").read_text(encoding="utf-8")
    embed_layout = (ROOT / "layouts/embeds/single.html").read_text(encoding="utf-8")

    assert "site.GetPage" in shortcode
    assert "Claracle Data Observatory" in partial
    assert "Embed attribution must keep this Claracle backlink visible" in partial
    assert "$title | htmlEscape" in partial
    assert "application/json" in partial
    assert "source_page" in embed_layout
    assert "robotsNoIndex" in (ROOT / "layouts/embeds/baseof.html").read_text(encoding="utf-8")


def test_copy_button_handles_clipboard_rejections() -> None:
    script = (ROOT / "assets/js/observatory-charts.js").read_text(encoding="utf-8")

    assert "try {" in script
    assert "await navigator.clipboard.writeText" in script
    assert "Copy failed" in script


def test_rendered_embed_contains_backlink_and_chart_data(tmp_path: Path) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render embed fixtures")

    rendered_site = tmp_path / "public"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(rendered_site)],
        cwd=ROOT,
        check=True,
    )

    embed_html = (
        rendered_site / "embeds/fastest-growing-ai-repositories-chart/index.html"
    ).read_text(encoding="utf-8")
    demo_html = (rendered_site / "charts/embeddable-rankings/index.html").read_text(
        encoding="utf-8"
    )

    assert "Claracle Data Observatory" in embed_html
    assert "https://claracle.com/data/fastest-growing-ai-repositories-this-year/" in embed_html
    assert "mattpocock/skills" in embed_html
    assert "observatory-chart__data" in embed_html
    assert "https://claracle.com/embeds/fastest-growing-ai-repositories-chart/" in demo_html
    assert "&lt;iframe" in demo_html
