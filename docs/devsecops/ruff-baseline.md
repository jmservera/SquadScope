# Ruff Baseline

> Issue: jmservera/SquadScope#540 (Phase A baseline) · jmservera/SquadScope#543 (Phase B fixes)
> Epic: jmservera/SquadScope-Coordinator#33
> Status: **Phase B complete** — `ruff check .` and `ruff format --check .` are clean.

Ruff is the Python linter/formatter for SquadScope. In Phase A it runs in CI as a
**non-blocking** job (`continue-on-error: true`) that emits GitHub annotations only.

## Configuration

See `[tool.ruff]` in `pyproject.toml`:

- `line-length = 100`
- `target-version = "py312"`
- Lint rule subset: `E` (pycodestyle errors), `F` (Pyflakes), `I` (import sorting)
- `ignore = ["E501"]` — line length is owned by the **formatter** (`ruff format`),
  enforced via `ruff format --check`. The lint-side E501 only fired on un-wrappable
  content (long URLs, prose inside triple-quoted string templates and test
  fixtures). This mirrors the standard Black/Ruff split.
- Vendored/generated/archived paths excluded (`.venv`, `node_modules`, `public`,
  `resources`, `themes`, `scripts/archived`, `.worktrees`)

## Phase A snapshot (resolved in Phase B)

- **Tool:** ruff 0.15.7
- **Date:** 2026-06-26
- **Total violations at baseline:** 1235 (129 auto-fixable)

| Count | Rule | Description | Phase B resolution |
|------:|------|-------------|--------------------|
| 1080 | E501 | line-too-long | `ruff format` wrapped code; residual content lines covered by `ignore` (formatter owns line length) |
|   65 | F401 | unused-import | `ruff check --fix` |
|   62 | I001 | unsorted-imports | `ruff check --fix` |
|   14 | E402 | module-import-not-at-top-of-file | `# noqa: E402` on `sys.path` bootstrap imports |
|    8 | F841 | unused-variable | removed dead assignments |
|    2 | E741 | ambiguous-variable-name | renamed `l` → `ln` |
|    2 | F541 | f-string-missing-placeholders | `ruff check --fix` |
|    1 | F402 | import-shadowed-by-loop-var | renamed loop variable |
|    1 | F821 | undefined-name | defined missing `DEFAULT_SYNTHESIS_MODEL` constant (latent bug) |

Current state: **`ruff check .` reports no violations.** Regenerate with
`ruff check . --statistics`.

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

- **Phase A:** baseline + non-blocking CI annotations. ✅
- **Phase B:** fix violations — ✅ all categories resolved; `ruff check`/`ruff format --check` clean.
- **Phase C:** pre-push hooks (#544) + blocking CI gate (#545). ✅ `Lint / Ruff`
  runs `ruff check` and `ruff format --check` in blocking mode; mark it required.
