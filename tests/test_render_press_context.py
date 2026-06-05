"""Tests for scripts/render_press_context.py."""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from render_press_context import (
    _extract_readme_description,
    _fetch_readme_snippet,
    _format_correlations_narrative,
    format_articles_list,
    format_correlations_list,
    format_divergences,
    render_press_context,
    resolve_paths,
)


# --- Fixtures ---


def _article(
    title="AI Startup Raises $10M",
    url="https://techcrunch.com/2026/05/15/ai-startup",
    categories=None,
    relevance_score=0.8,
    github_links=None,
):
    return {
        "title": title,
        "url": url,
        "categories": ["AI", "Startups"] if categories is None else categories,
        "relevance_score": relevance_score,
        "github_links": github_links or [],
        "entities": ["OpenAI"],
        "published_at": "2026-05-15T10:00:00Z",
        "summary": "A startup raised money.",
    }


def _correlation(
    repo="acme/cool-project",
    match_type="direct_link",
    confidence=0.9,
    hype_risk="low",
):
    return {
        "repo": repo,
        "press_correlated": True,
        "correlation_confidence": confidence,
        "matched_articles": ["https://techcrunch.com/article"],
        "match_type": match_type,
        "hype_risk": hype_risk,
    }


def _techcrunch_data(articles=None):
    arts = articles if articles is not None else [_article()]
    return {
        "week": "2026-W21",
        "source": "techcrunch",
        "crawled_at": "2026-05-19T10:00:00Z",
        "articles": arts,
        "metadata": {
            "total_articles": len(arts),
            "relevant_articles": len(arts),
            "github_links_found": 0,
        },
    }


def _correlation_data(correlations=None):
    corrs = correlations if correlations is not None else [_correlation()]
    return {
        "week": "2026-W21",
        "correlations": corrs,
        "uncorrelated_repos": [],
        "metadata": {
            "repos_analyzed": 10,
            "correlations_found": len(corrs),
            "articles_matched": 1,
        },
    }


# --- Tests ---


class TestFormatArticlesList:
    def test_empty(self):
        assert format_articles_list([]) == "- (none)"

    def test_single_article(self):
        result = format_articles_list([_article()])
        assert "[AI Startup Raises $10M]" in result
        assert _article()["url"] in result
        assert "[AI, Startups]" in result

    def test_article_without_url(self):
        art = _article(url="")
        result = format_articles_list([art])
        assert "AI Startup Raises $10M" in result
        assert "[](" not in result

    def test_article_without_categories(self):
        art = _article(categories=[])
        result = format_articles_list([art])
        assert "[AI, Startups]" not in result

    def test_multiple_articles(self):
        articles = [_article(title="First"), _article(title="Second")]
        result = format_articles_list(articles)
        assert "First" in result
        assert "Second" in result
        assert result.count("\n") == 1


class TestFormatCorrelationsList:
    def test_empty(self):
        assert format_correlations_list([]) == "- (none)"

    def test_single_correlation(self):
        result = format_correlations_list([_correlation()])
        assert "acme/cool-project" in result
        assert "direct_link" in result
        assert "0.9" in result
        assert "low" in result

    def test_multiple(self):
        corrs = [_correlation(repo="a/b"), _correlation(repo="c/d")]
        result = format_correlations_list(corrs)
        assert "a/b" in result
        assert "c/d" in result


class TestRenderPressContext:
    def test_no_data_returns_fallback(self):
        result = render_press_context(None, None, "2026-W21")
        assert "No press data available" in result
        assert "GitHub signals only" in result

    def test_with_techcrunch_only(self):
        result = render_press_context(_techcrunch_data(), None, "2026-W21")
        assert "Press Context" in result
        assert "2026-W21" in result
        assert "1 articles published" in result
        assert "0 repos have press correlation" in result

    def test_with_correlation_only(self):
        result = render_press_context(None, _correlation_data(), "2026-W21")
        assert "Press Context" in result
        assert "0 articles published" in result
        assert "1 repos have press correlation" in result

    def test_with_both(self):
        result = render_press_context(
            _techcrunch_data(), _correlation_data(), "2026-W21"
        )
        assert "1 articles published" in result
        assert "1 repos have press correlation" in result
        assert "AI Startup Raises $10M" in result
        assert "acme/cool-project" in result

    def test_filters_low_relevance_articles(self):
        low = _article(title="Irrelevant", relevance_score=0.2)
        high = _article(title="Relevant", relevance_score=0.8)
        tc = _techcrunch_data(articles=[low, high])
        result = render_press_context(tc, None, "2026-W21")
        assert "1 articles published" in result
        assert "Relevant" in result
        assert "Irrelevant" not in result

    def test_instructions_present(self):
        result = render_press_context(_techcrunch_data(), _correlation_data(), "2026-W21")
        assert "Press-correlated" in result
        assert "Organic growth" in result
        assert "Hype risk" in result
        assert "Press vs Reality" in result

    def test_hype_risk_labels(self):
        corr = _correlation(hype_risk="high")
        result = render_press_context(
            _techcrunch_data(), _correlation_data([corr]), "2026-W21"
        )
        assert "high" in result


class TestResolvePaths:
    def test_with_topic(self):
        tc, corr = resolve_paths("ai-ml", "2026-W21")
        assert "raw/ai-ml/2026-W21-external-news.json" in str(tc)
        assert "analyzed/ai-ml/2026-W21-correlations.json" in str(corr)

    def test_without_topic(self):
        tc, corr = resolve_paths(None, "2026-W99")
        assert "2026-W99-external-news.json" in str(tc)
        assert "2026-W99-correlations.json" in str(corr)

    def test_legacy_techcrunch_fallback(self):
        tc, corr = resolve_paths(None, "2026-W21")
        assert "2026-W21-techcrunch.json" in str(tc)
        assert "2026-W21-correlations.json" in str(corr)


class TestFormatCorrelationsListTopN:
    def _make_corrs(self, n: int) -> list[dict]:
        """Return n correlations with varying confidence/hype_risk."""
        risks = ["none", "low", "medium", "high"]
        return [
            {
                "repo": f"org/repo-{i}",
                "match_type": "keyword",
                "correlation_confidence": round(0.1 + 0.8 * i / max(n - 1, 1), 2),
                "hype_risk": risks[i % 4],
            }
            for i in range(n)
        ]

    def test_no_truncation_when_under_limit(self):
        corrs = self._make_corrs(5)
        result = format_correlations_list(corrs, top_n=10)
        assert "more repos with press correlation" not in result
        assert result.count("- org/repo") == 5

    def test_truncates_to_top_n(self):
        corrs = self._make_corrs(20)
        result = format_correlations_list(corrs, top_n=10)
        assert "…and 10 more repos with press correlation" in result
        assert result.count("- org/repo") == 10

    def test_sorted_by_confidence_desc(self):
        corrs = [
            {"repo": "low/conf", "match_type": "k", "correlation_confidence": 0.2, "hype_risk": "none"},
            {"repo": "high/conf", "match_type": "k", "correlation_confidence": 0.9, "hype_risk": "none"},
            {"repo": "mid/conf", "match_type": "k", "correlation_confidence": 0.5, "hype_risk": "none"},
        ]
        result = format_correlations_list(corrs, top_n=2)
        lines = [l for l in result.splitlines() if l.startswith("- ")]
        assert lines[0].startswith("- high/conf")
        assert lines[1].startswith("- mid/conf")
        assert "…and 1 more repos with press correlation" in result

    def test_no_top_n_returns_all(self):
        corrs = self._make_corrs(20)
        result = format_correlations_list(corrs)
        assert result.count("- org/repo") == 20
        assert "more repos" not in result


class TestFormatDivergencesReaderMode:
    def _divergences(self):
        return {
            "uncovered_tech_trends": [
                {
                    "topic": "quantum-computing",
                    "techcrunch_articles": [{"title": "Quantum Leap", "url": "https://tc.com/q"}],
                }
            ],
            "unpublicized_dev_activity": [
                {
                    "topic": "wasm-tooling",
                    "github_repos": [{"full_name": "org/wasm-lib", "stars": 500}],
                }
            ],
        }

    def test_ai_mode_has_instructions(self):
        result = format_divergences(self._divergences(), reader_mode=False)
        assert "#### Divergence Instructions" in result
        assert "Use divergences to identify" in result

    def test_reader_mode_no_instructions(self):
        result = format_divergences(self._divergences(), reader_mode=True)
        assert "#### Divergence Instructions" not in result
        assert "Use divergences to identify" not in result

    def test_reader_mode_has_narrative(self):
        result = format_divergences(self._divergences(), reader_mode=True)
        # Narrative prose paragraphs, no raw bullet lists
        assert "TechCrunch heavily covered" in result
        assert "Developer activity this week" in result
        assert "- **quantum-computing**:" not in result
        assert "- **wasm-tooling**:" not in result

    def test_reader_mode_has_repo_links(self):
        result = format_divergences(self._divergences(), reader_mode=True)
        # Repo name as link, not full_name with stars
        assert "[wasm-lib](https://github.com/org/wasm-lib)" in result
        # Article link preserved
        assert "[Quantum Leap](https://tc.com/q)" in result

    def test_reader_mode_still_shows_data(self):
        result = format_divergences(self._divergences(), reader_mode=True)
        assert "quantum-computing" in result
        assert "wasm-tooling" in result


class TestRenderPressContextReaderMode:
    def test_reader_mode_removes_instructions_block(self):
        result = render_press_context(
            _techcrunch_data(), _correlation_data(), "2026-W21", reader_mode=True
        )
        assert "### Instructions" not in result
        assert "Press-correlated" not in result
        assert "Press vs Reality" not in result

    def test_ai_mode_keeps_instructions_block(self):
        result = render_press_context(
            _techcrunch_data(), _correlation_data(), "2026-W21", reader_mode=False
        )
        assert "### Instructions" in result
        assert "Press-correlated" in result

    def test_reader_mode_uses_narrative(self):
        many = [
            {
                "repo": f"openai/repo-{i}",
                "match_type": "org_name",
                "correlation_confidence": 0.8,
                "hype_risk": "medium",
                "matched_articles": ["https://techcrunch.com/article"],
            }
            for i in range(20)
        ]
        tc = _techcrunch_data([_article(title="OpenAI Launch", url="https://techcrunch.com/article")])
        result = render_press_context(tc, _correlation_data(many), "2026-W21", reader_mode=True)
        # Narrative mode: no raw confidence/match_type bullets
        assert "confidence:" not in result
        assert "match_type" not in result
        # Should contain prose with repo links
        assert "https://github.com/openai/repo-" in result

    def test_reader_mode_no_raw_confidence_in_narrative(self):
        few = [
            {
                "repo": f"google/repo-{i}",
                "match_type": "org_name",
                "correlation_confidence": 0.9,
                "hype_risk": "low",
                "matched_articles": [],
            }
            for i in range(5)
        ]
        result = render_press_context(
            _techcrunch_data(),
            _correlation_data(few),
            "2026-W21",
            reader_mode=True,
        )
        assert "confidence:" not in result
        assert "more repos with press correlation" not in result
        assert "https://github.com/google/repo-" in result


class TestStripAiInstructions:
    """Tests for analyze_fallback._strip_ai_instructions."""

    def setup_method(self):
        import sys
        sys.path.insert(0, str(_REPO_ROOT))
        import scripts.analyze_fallback as af
        self.af = af

    def _full_press_context(self) -> str:
        """Simulate a fully rendered AI-mode press context."""
        return (
            "## Press Context (TechCrunch, week of 2026-W21)\n"
            "3 articles published relevant to tech/open-source.\n\n"
            "Notable coverage:\n"
            "- [Article One](https://tc.com/1) [AI]\n\n"
            "### Correlation Summary\n"
            "15 repos have press correlation:\n"
            + "\n".join(
                f"- org/repo-{i} — match: keyword, confidence: 0.5, hype_risk: low"
                for i in range(15)
            )
            + "\n\n"
            "### Instructions\n"
            "For each trending repo, note if press coverage preceded the star surge.\n"
            "Label repos as:\n"
            "- '📰 Press-correlated' — stars gained after/during press coverage\n"
            "- '🌱 Organic growth' — stars gained without press coverage\n"
        )

    def test_removes_instructions_section(self):
        content = self._full_press_context()
        result = self.af._strip_ai_instructions(content)
        assert "### Instructions" not in result
        assert "Press-correlated" not in result

    def test_removes_divergence_instructions(self):
        content = (
            "### Divergence Analysis\n\n"
            "#### 🚀 Dev Activity Without Press Coverage\n"
            "repos...\n\n"
            "#### Divergence Instructions\n"
            "Use divergences to identify:\n"
            "- 🔮 Where industry is moving\n"
            "- 💡 Where devs are innovating\n"
        )
        result = self.af._strip_ai_instructions(content)
        assert "#### Divergence Instructions" not in result
        assert "Use divergences to identify" not in result

    def test_truncates_correlation_list_to_10(self):
        content = self._full_press_context()
        result = self.af._strip_ai_instructions(content)
        repo_lines = [ln for ln in result.splitlines() if ln.startswith("- org/repo")]
        assert len(repo_lines) == 10
        assert "…and 5 more repos with press correlation" in result

    def test_no_truncation_when_under_limit(self):
        content = (
            "### Correlation Summary\n"
            "5 repos have press correlation:\n"
            + "\n".join(
                f"- org/repo-{i} — match: keyword, confidence: 0.5, hype_risk: low"
                for i in range(5)
            )
            + "\n"
        )
        result = self.af._strip_ai_instructions(content)
        assert "more repos with press correlation" not in result
        assert result.count("- org/repo") == 5


class TestExtractReadmeDescription:
    def test_returns_first_readable_line(self):
        snippet = "# My Project\n\nA fast, zero-dependency library for data processing.\n"
        assert _extract_readme_description(snippet) == "A fast, zero-dependency library for data processing"

    def test_skips_heading_lines(self):
        snippet = "# Heading\n## Subheading\nActual description here.\n"
        assert _extract_readme_description(snippet) == "Actual description here"

    def test_skips_image_badge_lines(self):
        snippet = "[![badge](img)](url)\nA concise description of what this library does.\n"
        assert _extract_readme_description(snippet) == "A concise description of what this library does"

    def test_returns_empty_on_no_match(self):
        assert _extract_readme_description("# Only a heading\n") == ""

    def test_strips_markdown_links(self):
        snippet = "Check out [our docs](https://example.com) for more information.\n"
        result = _extract_readme_description(snippet)
        assert "https://example.com" not in result
        assert "our docs" in result


class TestFormatCorrelationsNarrative:
    def _corr(self, repo="openai/codex", confidence=0.8, hype_risk="medium", articles=None):
        return {
            "repo": repo,
            "press_correlated": True,
            "correlation_confidence": confidence,
            "matched_articles": articles or [],
            "match_type": "org_name",
            "hype_risk": hype_risk,
        }

    def _art(self, title="OpenAI News", url="https://techcrunch.com/openai-news"):
        return {"title": title, "url": url, "categories": ["AI"]}

    def test_empty_returns_fallback(self):
        result = _format_correlations_narrative([], [])
        assert "No significant press correlations" in result

    def test_produces_repo_links(self):
        corr = self._corr(repo="openai/codex", articles=["https://techcrunch.com/a1"])
        result = _format_correlations_narrative([corr], [self._art(url="https://techcrunch.com/a1")])
        assert "[codex](https://github.com/openai/codex)" in result

    def test_produces_article_links_when_title_available(self):
        corr = self._corr(articles=["https://techcrunch.com/a1"])
        art = self._art(title="OpenAI Launches Codex", url="https://techcrunch.com/a1")
        result = _format_correlations_narrative([corr], [art])
        assert "[OpenAI Launches Codex](https://techcrunch.com/a1)" in result

    def test_no_raw_confidence_in_output(self):
        corr = self._corr()
        result = _format_correlations_narrative([corr], [])
        assert "confidence:" not in result
        assert "match_type" not in result
        assert "hype_risk" not in result

    def test_groups_by_org(self):
        corrs = [
            self._corr(repo="openai/codex"),
            self._corr(repo="openai/gpt-4"),
            self._corr(repo="google/material-design-icons", confidence=0.5),
        ]
        result = _format_correlations_narrative(corrs, [])
        # openai dominates — should appear in first paragraph
        assert "openai" in result.lower()
        assert "google" in result.lower()

    def test_no_article_link_when_url_not_in_articles(self):
        corr = self._corr(articles=["https://techcrunch.com/unknown-url"])
        result = _format_correlations_narrative([corr], [])
        # URL is in the corr but not in the articles list, so no link text
        # Any links present must point to github.com (repo links), not article URLs
        link_urls = re.findall(r'\]\((https?://[^)]+)\)', result)
        assert all(urlparse(url).netloc == "github.com" for url in link_urls)

    def test_reader_mode_true_uses_narrative(self):
        corr = self._corr(repo="openai/codex")
        result = format_correlations_list([corr], reader_mode=True, articles=[])
        assert "confidence:" not in result
        assert "[codex](https://github.com/openai/codex)" in result

    def test_reader_mode_false_uses_bullet_list(self):
        corr = self._corr(repo="openai/codex")
        result = format_correlations_list([corr], reader_mode=False)
        assert "openai/codex" in result
        assert "confidence:" in result
        assert "match:" in result

    def test_ai_mode_unchanged_in_render(self):
        tc = _techcrunch_data()
        corr_data = _correlation_data([self._corr()])
        result = render_press_context(tc, corr_data, "2026-W21", reader_mode=False)
        assert "confidence:" in result
        assert "### Instructions" in result


class TestReaderModeCountHeader:
    """reader_mode=True must not emit the raw 'N repos have press correlation:' header."""

    def _corrs(self, n: int = 5) -> list[dict]:
        return [
            {
                "repo": f"openai/repo-{i}",
                "match_type": "org_name",
                "correlation_confidence": 0.8,
                "hype_risk": "low",
                "matched_articles": [],
            }
            for i in range(n)
        ]

    def test_reader_mode_omits_count_header(self):
        tc = {"articles": []}
        corr_data = {"correlations": self._corrs(5), "divergences": {}}
        result = render_press_context(tc, corr_data, "2026-W21", reader_mode=True)
        assert "repos have press correlation" not in result

    def test_ai_mode_keeps_count_header(self):
        tc = {"articles": []}
        corr_data = {"correlations": self._corrs(5), "divergences": {}}
        result = render_press_context(tc, corr_data, "2026-W21", reader_mode=False)
        assert "repos have press correlation" in result


class TestExtractReadmeDescriptionSentenceBoundary:
    """_extract_readme_description must not return mid-sentence truncated text."""

    def test_drops_line_without_sentence_boundary(self):
        # Simulates a 500-char truncation mid-sentence
        snippet = "# Guava\n\nGuava is a set of core Java libraries from Google that includes new collect"
        result = _extract_readme_description(snippet)
        assert result == ""

    def test_trims_to_last_sentence_in_long_line(self):
        snippet = (
            "# Lib\n\n"
            "This library does X. It also does Y. And even more beyond that without end"
        )
        result = _extract_readme_description(snippet)
        # Should trim to the last complete sentence boundary
        assert result == "This library does X. It also does Y"

    def test_returns_empty_when_no_boundary_in_snippet(self):
        snippet = "# Header\n\nNo period here at all and the line is long enough to match normally"
        result = _extract_readme_description(snippet)
        assert result == ""
