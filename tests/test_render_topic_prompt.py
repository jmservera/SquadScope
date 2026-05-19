"""Tests for scripts/render_topic_prompt.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.render_topic_prompt import (
    load_wisdom,
    render_template,
    _remove_blocks,
    _keep_blocks,
)


SAMPLE_TEMPLATE = """\
# Analysis

{{#IF_TOPIC}}
Topic: {{TOPIC_NAME}}
Description: {{TOPIC_DESCRIPTION}}
ID: {{TOPIC_ID}}
Wisdom: {{WISDOM_CONTENT}}
{{/IF_TOPIC}}
{{#IF_NO_TOPIC}}
General analysis mode.
{{/IF_NO_TOPIC}}

## Common section
This appears always.
"""


class TestRenderTemplateWithTopic:
    """Template renders correctly when topic config is provided."""

    def test_topic_placeholders_replaced(self):
        config = {"id": "ai-ml", "name": "AI/ML", "description": "Artificial intelligence and machine learning"}
        rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "AI/ML" in rendered
        assert "Artificial intelligence and machine learning" in rendered
        assert "ai-ml" in rendered

    def test_if_topic_block_included(self):
        config = {"id": "devops", "name": "DevOps", "description": "CI/CD and infrastructure"}
        rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "Topic: DevOps" in rendered
        assert "Description: CI/CD and infrastructure" in rendered

    def test_if_no_topic_block_removed(self):
        config = {"id": "devops", "name": "DevOps", "description": "CI/CD and infrastructure"}
        rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "General analysis mode." not in rendered

    def test_common_section_preserved(self):
        config = {"id": "security", "name": "Security", "description": "AppSec and infra security"}
        rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "## Common section" in rendered
        assert "This appears always." in rendered

    def test_wisdom_placeholder_filled_when_no_wisdom_file(self):
        config = {"id": "nonexistent-topic", "name": "Test", "description": "Test topic"}
        rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "(No per-topic wisdom accumulated yet.)" in rendered

    def test_wisdom_content_injected(self):
        config = {"id": "ai-ml", "name": "AI/ML", "description": "AI stuff"}
        wisdom_text = "Look for transformer architectures and real benchmarks."

        with patch("scripts.render_topic_prompt.load_wisdom", return_value=wisdom_text):
            rendered = render_template(SAMPLE_TEMPLATE, config)

        assert "Look for transformer architectures" in rendered

    def test_frontmatter_topic_field(self):
        template_with_frontmatter = """\
{{#IF_TOPIC}}
   - `topic` (value: `{{TOPIC_ID}}`)
{{/IF_TOPIC}}
"""
        config = {"id": "rust", "name": "Rust", "description": "Rust ecosystem"}
        rendered = render_template(template_with_frontmatter, config)

        assert "`rust`" in rendered


class TestRenderTemplateWithoutTopic:
    """Template works without topic config (backward compatibility)."""

    def test_none_config_uses_general_mode(self):
        rendered = render_template(SAMPLE_TEMPLATE, None)

        assert "General analysis mode." in rendered

    def test_empty_config_uses_general_mode(self):
        rendered = render_template(SAMPLE_TEMPLATE, {})

        assert "General analysis mode." in rendered

    def test_topic_blocks_removed(self):
        rendered = render_template(SAMPLE_TEMPLATE, None)

        assert "{{TOPIC_NAME}}" not in rendered
        assert "{{TOPIC_DESCRIPTION}}" not in rendered
        assert "{{TOPIC_ID}}" not in rendered

    def test_common_section_preserved(self):
        rendered = render_template(SAMPLE_TEMPLATE, None)

        assert "## Common section" in rendered
        assert "This appears always." in rendered

    def test_no_conditional_markers_remain(self):
        rendered = render_template(SAMPLE_TEMPLATE, None)

        assert "{{#IF_TOPIC}}" not in rendered
        assert "{{/IF_TOPIC}}" not in rendered
        assert "{{#IF_NO_TOPIC}}" not in rendered
        assert "{{/IF_NO_TOPIC}}" not in rendered


class TestLoadWisdom:
    """Missing wisdom file handled gracefully."""

    def test_missing_wisdom_returns_empty(self):
        result = load_wisdom("topic-that-does-not-exist-xyz")
        assert result == ""

    def test_none_topic_id_returns_empty(self):
        result = load_wisdom(None)
        assert result == ""

    def test_empty_topic_id_returns_empty(self):
        result = load_wisdom("")
        assert result == ""


class TestBlockHelpers:
    """Unit tests for block manipulation helpers."""

    def test_remove_blocks(self):
        text = "before\n{{#FOO}}\ninner\n{{/FOO}}\nafter"
        result = _remove_blocks(text, "FOO")
        assert "inner" not in result
        assert "before" in result
        assert "after" in result

    def test_keep_blocks(self):
        text = "before\n{{#FOO}}\ninner\n{{/FOO}}\nafter"
        result = _keep_blocks(text, "FOO")
        assert "inner" in result
        assert "{{#FOO}}" not in result
        assert "{{/FOO}}" not in result
