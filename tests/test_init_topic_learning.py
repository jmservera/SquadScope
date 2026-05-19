"""Tests for scripts/init_topic_learning.py"""

from pathlib import Path

import pytest

from scripts.init_topic_learning import init_topic, SEEDED_WISDOM


@pytest.fixture
def base_dir(tmp_path):
    return tmp_path / ".squad"


class TestInitTopic:
    def test_creates_directory_structure(self, base_dir):
        root = init_topic("ai-ml", base_dir=base_dir)

        assert root == base_dir / "topics" / "ai-ml"
        assert (root / "skills").is_dir()
        assert (root / "scorecards").is_dir()
        assert (root / "wisdom.md").is_file()

    def test_seeds_wisdom_for_known_topic(self, base_dir):
        init_topic("ai-ml", base_dir=base_dir)
        content = (base_dir / "topics" / "ai-ml" / "wisdom.md").read_text()

        assert "Signal Patterns" in content
        assert "arXiv references" in content

    def test_seeds_wisdom_for_rust(self, base_dir):
        init_topic("rust", base_dir=base_dir)
        content = (base_dir / "topics" / "rust" / "wisdom.md").read_text()

        assert "CLI tools that replace existing Unix utilities" in content
        assert "Cargo ecosystem" in content

    def test_unknown_topic_gets_default_wisdom(self, base_dir):
        init_topic("golang", base_dir=base_dir)
        content = (base_dir / "topics" / "golang" / "wisdom.md").read_text()

        assert "golang Topic Wisdom" in content

    def test_idempotent_does_not_overwrite(self, base_dir):
        init_topic("ai-ml", base_dir=base_dir)
        wisdom = base_dir / "topics" / "ai-ml" / "wisdom.md"
        wisdom.write_text("custom content")

        # Second run without force should preserve custom content
        init_topic("ai-ml", base_dir=base_dir)
        assert wisdom.read_text() == "custom content"

    def test_force_overwrites_existing(self, base_dir):
        init_topic("ai-ml", base_dir=base_dir)
        wisdom = base_dir / "topics" / "ai-ml" / "wisdom.md"
        wisdom.write_text("custom content")

        init_topic("ai-ml", force=True, base_dir=base_dir)
        assert wisdom.read_text() == SEEDED_WISDOM["ai-ml"]

    def test_multiple_runs_safe(self, base_dir):
        """Running multiple times doesn't raise errors."""
        init_topic("ai-ml", base_dir=base_dir)
        init_topic("ai-ml", base_dir=base_dir)
        init_topic("ai-ml", base_dir=base_dir)

        assert (base_dir / "topics" / "ai-ml" / "wisdom.md").is_file()
