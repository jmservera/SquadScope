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
    errors: list[str] = []
    for prompt_file in sorted(PROMPTS_DIR.glob("*.md")):
        errors.extend(lint_prompt(prompt_file))

    assert not errors, (
        f"{len(errors)} prompt security issue(s):\n" + "\n".join(errors)
    )
