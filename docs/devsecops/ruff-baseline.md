# Ruff Baseline (Phase A — warning-only)

> Issue: jmservera/SquadScope#540 · Epic: jmservera/SquadScope-Coordinator#33
> Mode: **warning-only / non-blocking**. Do not fix (Phase B) or enforce (Phase C) yet.

Ruff is the Python linter/formatter for SquadScope. In Phase A it runs in CI as a
**non-blocking** job (`continue-on-error: true`) that emits GitHub annotations only.

## Configuration

See `[tool.ruff]` in `pyproject.toml`:

- `line-length = 100`
- `target-version = "py312"`
- Lint rule subset: `E` (pycodestyle errors), `F` (Pyflakes), `I` (import sorting)
- Vendored/generated/archived paths excluded (`.venv`, `node_modules`, `public`,
  `resources`, `themes`, `scripts/archived`, `.worktrees`)

## Baseline snapshot

- **Tool:** ruff 0.15.7
- **Date:** 2026-06-26
- **Total violations:** 1235 (129 auto-fixable)

| Count | Rule | Description |
|------:|------|-------------|
| 1080 | E501 | line-too-long |
|   65 | F401 | unused-import |
|   62 | I001 | unsorted-imports |
|   14 | E402 | module-import-not-at-top-of-file |
|    8 | F841 | unused-variable |
|    2 | E741 | ambiguous-variable-name |
|    2 | F541 | f-string-missing-placeholders |
|    1 | F402 | import-shadowed-by-loop-var |
|    1 | F821 | undefined-name |

Regenerate with: `ruff check . --statistics`

## Running locally

```bash
# Install (pinned to match CI)
pip install ruff==0.15.7

# Lint the repository (report only)
ruff check .

# Show counts by rule
ruff check . --statistics

# Auto-fix the safe subset (Phase B work — do not bulk-apply in Phase A)
ruff check . --fix

# Format check / apply (not enforced in Phase A)
ruff format --check .
ruff format .
```

## Phase plan

- **Phase A (now):** baseline + non-blocking CI annotations. ← this PR
- **Phase B:** fix violations (start with auto-fixable F401/I001/F541).
- **Phase C:** pre-push hooks + blocking required status check.
