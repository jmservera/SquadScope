"""CI test wrapper for the prompt security linter.

Ensures prompt templates maintain security guardrails on every PR. Fails if
any prompt template has unguarded external variables, missing closing security
constraints, or unknown/unclassified template variables.
"""

from pathlib import Path

from scripts.lint_prompts import lint_prompt


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def test_all_prompts_pass_security_lint():
    """All prompt templates must pass the security linter."""
    prompt_files = sorted(PROMPTS_DIR.glob("*.md"))
    assert prompt_files, (
        f"No prompt templates found in {PROMPTS_DIR}; "
        "expected at least one .md file to lint"
    )
    errors: list[str] = []
    for prompt_file in prompt_files:
        errors.extend(lint_prompt(prompt_file))

    assert not errors, (
        f"{len(errors)} prompt security issue(s):\n" + "\n".join(errors)
    )
