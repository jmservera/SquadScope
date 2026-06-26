from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_weekly_article_footer_has_prefilled_correction_report_link() -> None:
    footer = (ROOT / "layouts/partials/article-footer.html").read_text(encoding="utf-8")

    assert "Correction report: %s" in footer
    assert "Article: %s" in footer
    assert "Week: %s" in footer
    assert "issues/new?title=%s&body=%s&labels=%s" in footer
    assert "correction,reader-report" in footer
    assert "Suggested labels for maintainers" in footer
    assert "report a correction, source concern, or safety concern" in footer


def test_methodology_page_documents_corrections_and_responsible_ai_limits() -> None:
    methodology = (ROOT / "content/methodology/_index.md").read_text(encoding="utf-8")

    assert "## Responsible-AI caveats and bias limits" in methodology
    assert "**Source bias:**" in methodology
    assert "**English-language source bias:**" in methodology
    assert "**Platform bias:**" in methodology
    assert "not be read as a neutral or complete map" in methodology
    assert "## Corrections and reader reports" in methodology
    assert "Leave visible correction notes" in methodology
    assert "`errata` entry" in methodology


def test_methodology_is_in_navigation_and_distribution_guidance() -> None:
    hugo_config = (ROOT / "hugo.toml").read_text(encoding="utf-8")
    distribution = (ROOT / "docs/growth/distribution-strategy.md").read_text(encoding="utf-8")

    assert "identifier = 'methodology'" in hugo_config
    assert "url = '/methodology/'" in hugo_config
    assert "Methodology and corrections policy" in distribution
    assert "https://www.claracle.com/methodology/" in distribution
    assert "Do not promote an article as neutral or comprehensive" in distribution
