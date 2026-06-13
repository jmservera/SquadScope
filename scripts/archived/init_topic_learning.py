#!/usr/bin/env python3
"""Initialize per-topic learning state directories with seeded wisdom."""

import argparse
import sys
from pathlib import Path

import yaml

SQUAD_DIR = Path(".squad")

SEEDED_WISDOM = {
    "ai-ml": """\
# AI & Machine Learning Topic Wisdom

## Signal Patterns
- Papers with code implementations gain rapid adoption
- Framework-adjacent tools (PyTorch/TensorFlow ecosystem) show sustained growth
- LLM-related repos have high initial stars but variable retention
- Research reproducibility repos (paper implementations) peak early then plateau

## Noise Patterns
- Tutorial/course repos with high stars but low forks are often one-time views
- Wrapper libraries around APIs tend to be ephemeral
- Repos that only add a README without substantial code are often hype-driven

## Scoring Adjustments
- Weight Python and Jupyter Notebook repos higher
- Look for arXiv references as quality signals
- Multi-language repos (Python + C++) often indicate serious frameworks
""",
    "rust": """\
# Rust Topic Wisdom

## Signal Patterns
- CLI tools that replace existing Unix utilities gain rapid adoption
- Async runtime ecosystem tools show sustained growth
- WebAssembly-targeting Rust projects are emerging strongly
- Safety-focused alternatives to C/C++ libraries gain institutional backing

## Noise Patterns
- "Rewrite in Rust" repos without clear improvements over originals
- Learning projects with "rust-" prefix but minimal functionality
- Abandoned experimental repos from Rust newcomers

## Scoring Adjustments
- Weight Rust language repos exclusively
- Cross-compilation and no_std support indicate maturity
- Cargo ecosystem integration (published crate) is a strong signal
""",
}


def init_topic(topic_id: str, *, force: bool = False, base_dir: Path | None = None) -> Path:
    """Create learning state directory structure for a topic.

    Returns the created topic directory path.
    """
    root = (base_dir or SQUAD_DIR) / "topics" / topic_id
    skills_dir = root / "skills"
    scorecards_dir = root / "scorecards"
    wisdom_file = root / "wisdom.md"

    # Create directories
    skills_dir.mkdir(parents=True, exist_ok=True)
    scorecards_dir.mkdir(parents=True, exist_ok=True)

    # Seed wisdom
    if force or not wisdom_file.exists():
        content = SEEDED_WISDOM.get(topic_id, f"# {topic_id} Topic Wisdom\n")
        wisdom_file.write_text(content)

    return root


def topic_id_from_config(config_path: str) -> str:
    """Read topic.id from a YAML config file."""
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return data["topic"]["id"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Initialize per-topic learning state")
    parser.add_argument("--topic", help="Topic ID to initialize")
    parser.add_argument("--config", help="Path to topic YAML config (reads topic.id)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing wisdom")

    args = parser.parse_args(argv)

    if not args.topic and not args.config:
        parser.error("Provide --topic or --config")

    topic_id = args.topic or topic_id_from_config(args.config)
    root = init_topic(topic_id, force=args.force)
    print(f"Initialized learning state: {root}")


if __name__ == "__main__":
    main()
