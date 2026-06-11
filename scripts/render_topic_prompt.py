#!/usr/bin/env python3
"""Render the topic-aware analysis prompt template with values from squadscope.topic.yml.

Usage:
    python scripts/render_topic_prompt.py [--config PATH] [--output PATH]

If --config is not provided, looks for squadscope.topic.yml in the repo root.
If --output is not provided, prints to stdout.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Use PyYAML if available, otherwise fall back to a minimal inline parser
try:
    import yaml  # type: ignore[import-untyped]

    def _load_yaml(path: Path) -> dict:
        with open(path) as f:
            return yaml.safe_load(f) or {}

except ImportError:
    # Minimal YAML subset parser for simple key: value files
    def _load_yaml(path: Path) -> dict:  # type: ignore[misc]
        result: dict = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    result[key] = value
        return result


def find_repo_root() -> Path:
    """Walk up from CWD to find the git repo root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_topic_config(config_path: Path | None) -> dict | None:
    """Load topic configuration from YAML. Returns None if not found."""
    if config_path and config_path.exists():
        return _load_yaml(config_path)

    # Try default location
    root = find_repo_root()
    default_path = root / "squadscope.topic.yml"
    if default_path.exists():
        return _load_yaml(default_path)

    return None


def load_wisdom(topic_id: str | None) -> str:
    """Load per-topic wisdom file if it exists."""
    if not topic_id:
        return ""

    # Reject topic IDs that could escape the topics/ directory.
    import re
    if not re.fullmatch(r"[a-z0-9][a-z0-9\-_]{0,63}", topic_id):
        return ""

    root = find_repo_root()
    wisdom_path = root / "topics" / topic_id / "wisdom.md"
    # Containment check: ensure the resolved path stays inside topics/
    topics_root = (root / "topics").resolve()
    try:
        wisdom_path.resolve().relative_to(topics_root)
    except ValueError:
        return ""
    if wisdom_path.exists():
        return wisdom_path.read_text(encoding="utf-8").strip()

    return ""


def render_template(template: str, topic_config: dict | None) -> str:
    """Render the topic-aware prompt template with config values.

    Handles conditional blocks:
      {{#IF_TOPIC}}...{{/IF_TOPIC}} — included only when topic config is present
      {{#IF_NO_TOPIC}}...{{/IF_NO_TOPIC}} — included only when topic config is absent
    """
    has_topic = topic_config is not None and bool(topic_config.get("id") or topic_config.get("name"))

    if has_topic:
        topic_id = topic_config.get("id", "")
        topic_name = topic_config.get("name", "")
        topic_description = topic_config.get("description", "")
        wisdom_content = load_wisdom(topic_id)

        # Sanitize user-controlled topic fields
        from sanitize_repo_content import sanitize_text

        topic_name = sanitize_text(topic_name, max_length=200, label="topic_name")
        topic_description = sanitize_text(
            topic_description, max_length=500, label="topic_description"
        )

        # Remove IF_NO_TOPIC blocks
        rendered = _remove_blocks(template, "IF_NO_TOPIC")
        # Keep IF_TOPIC block contents
        rendered = _keep_blocks(rendered, "IF_TOPIC")

        # Replace placeholders
        rendered = rendered.replace("{{TOPIC_ID}}", topic_id)
        rendered = rendered.replace("{{TOPIC_NAME}}", topic_name)
        rendered = rendered.replace("{{TOPIC_DESCRIPTION}}", topic_description)
        rendered = rendered.replace("{{WISDOM_CONTENT}}", wisdom_content if wisdom_content else "(No per-topic wisdom accumulated yet.)")
    else:
        # Remove IF_TOPIC blocks
        rendered = _remove_blocks(template, "IF_TOPIC")
        # Keep IF_NO_TOPIC block contents
        rendered = _keep_blocks(rendered, "IF_NO_TOPIC")

        # Clear any remaining topic placeholders
        rendered = rendered.replace("{{TOPIC_ID}}", "")
        rendered = rendered.replace("{{TOPIC_NAME}}", "")
        rendered = rendered.replace("{{TOPIC_DESCRIPTION}}", "")
        rendered = rendered.replace("{{WISDOM_CONTENT}}", "")

    return rendered


def _remove_blocks(text: str, block_name: str) -> str:
    """Remove conditional block markers and their contents."""
    start_tag = "{{#" + block_name + "}}"
    end_tag = "{{/" + block_name + "}}"

    result = text
    while start_tag in result:
        start_idx = result.index(start_tag)
        end_idx = result.index(end_tag) + len(end_tag)
        # Remove trailing newline if present
        if end_idx < len(result) and result[end_idx] == "\n":
            end_idx += 1
        result = result[:start_idx] + result[end_idx:]

    return result


def _keep_blocks(text: str, block_name: str) -> str:
    """Remove conditional block markers but keep their contents."""
    start_tag = "{{#" + block_name + "}}"
    end_tag = "{{/" + block_name + "}}"

    result = text.replace(start_tag + "\n", "").replace(start_tag, "")
    result = result.replace(end_tag + "\n", "").replace(end_tag, "")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Render topic-aware analysis prompt template")
    parser.add_argument("--config", type=Path, help="Path to squadscope.topic.yml")
    parser.add_argument("--output", type=Path, help="Output file path (default: stdout)")
    parser.add_argument("--template", type=Path, help="Template file (default: prompts/analyze-topic.md)")
    args = parser.parse_args()

    root = find_repo_root()

    # Load template
    template_path = args.template or (root / "prompts" / "analyze-topic.md")
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    template = template_path.read_text(encoding="utf-8")

    # Load topic config
    topic_config = load_topic_config(args.config)

    # Render
    rendered = render_template(template, topic_config)

    # Output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
