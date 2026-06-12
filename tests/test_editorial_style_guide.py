"""Validate the editorial style guide contains all required safety sections.

This test ensures the Signal Check editorial style guide maintains required
safety boundaries, disclosure requirements, and structural constraints that
prevent unsafe content generation.
"""

from pathlib import Path

import pytest

GUIDE_PATH = Path(__file__).resolve().parent.parent / "docs" / "editorial-style-guide.md"


@pytest.fixture
def guide_content() -> str:
    assert GUIDE_PATH.exists(), f"Editorial style guide not found at {GUIDE_PATH}"
    return GUIDE_PATH.read_text(encoding="utf-8")


class TestEditorialStyleGuideStructure:
    """Verify the guide contains all required structural elements."""

    def test_guide_exists(self):
        assert GUIDE_PATH.exists()

    def test_has_host_roles(self, guide_content: str):
        assert "Host A" in guide_content
        assert "Host B" in guide_content
        assert "Curator" in guide_content
        assert "Skeptic" in guide_content

    def test_has_all_segments(self, guide_content: str):
        required_segments = [
            "Cold Open",
            "The Signal",
            "The Noise Check",
            "The Gap",
            "Receipts Round",
            "Week Ahead",
            "Outro",
        ]
        for segment in required_segments:
            assert segment in guide_content, f"Missing segment: {segment}"

    def test_has_word_count_target(self, guide_content: str):
        assert "1,200" in guide_content
        assert "1,700" in guide_content


class TestEditorialStyleGuideSafety:
    """Verify safety boundaries are documented."""

    def test_ai_disclosure_requirement(self, guide_content: str):
        assert "first 60 seconds" in guide_content.lower() or "first 60 seconds" in guide_content
        assert "AI-generated voice" in guide_content or "ai_generated" in guide_content

    def test_prohibited_content_section(self, guide_content: str):
        required_prohibitions = [
            "Real-person mimicry",
            "Copied expression",
            "Unsupported facts",
            "Defamatory motive",
            "Fake sponsorship",
            "Individual-targeting humor",
        ]
        for prohibition in required_prohibitions:
            assert prohibition in guide_content, f"Missing prohibition: {prohibition}"

    def test_corrections_path(self, guide_content: str):
        assert "corrections" in guide_content.lower()
        assert "github.com" in guide_content

    def test_claim_ledger_requirement(self, guide_content: str):
        assert "claim ledger" in guide_content.lower()
        assert "must map" in guide_content.lower() or "MUST map" in guide_content

    def test_distinctiveness_requirements(self, guide_content: str):
        assert "Hard Fork" in guide_content
        assert "must NOT replicate" in guide_content or "must not replicate" in guide_content.lower()

    def test_sponsorship_guardrails(self, guide_content: str):
        assert "FTC" in guide_content or "sponsorship" in guide_content.lower()
        assert "brought to you by" in guide_content.lower()
