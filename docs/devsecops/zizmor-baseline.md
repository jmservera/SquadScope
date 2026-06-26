# Zizmor Baseline

> Issue: jmservera/SquadScope#542 (Phase A) · jmservera/SquadScope#543 (Phase B fixes)
> Epic: jmservera/SquadScope-Coordinator#33
> Status: **Phase B complete** for High-severity — 0 high/medium findings; CI
> (default persona) is clean. Remaining pedantic info/low items are documented below.

[zizmor](https://github.com/zizmorcore/zizmor) audits GitHub Actions workflows
for supply-chain risks (template injection, dangerous triggers, unpinned actions,
excessive permissions). It **already exists** in
`.github/workflows/security-scanning.yml` (`zizmorcore/zizmor-action`). This task
normalizes it to the Phase-A contract — it does **not** recreate the job.

## CI wiring (confirmed)

- **Job:** `zizmor-scan` in `.github/workflows/security-scanning.yml`.
- **Triggers:** push + pull_request to `main`/`dev` — so it runs on any change to
  `.github/workflows/`.
- **Non-blocking:** `continue-on-error: true` (Phase A warning-only).
- **SARIF / annotations:** `advanced-security: true` uploads SARIF to GitHub Code
  Scanning automatically.
- **Scope:** all repository-owned workflows, excluding generated `squad-*` and
  `sync-squad-labels` files.

## Baseline snapshot

- **Tool:** zizmor 1.25.2
- **Date:** 2026-06-26
- **Scope:** repo-owned workflows (Squad-generated files excluded)

### Default (`regular`) persona — what CI surfaces today

**0 actionable findings** (7 ignored, 42 suppressed). The Phase-A gate is green
on the default persona; the action focuses on P0 findings (template-injection,
dangerous-triggers), of which there are none.

### Deep (`pedantic`) persona — Phase B progress

| Rule | Severity | Phase A | Now | Phase B resolution |
|------|----------|--------:|----:|--------------------|
| excessive-permissions | High | 4 | **0** | Moved workflow-level write `permissions:` to job level (`copilot-pricing-review`, `restore-publish-backup`, `sync-publish-to-main`) |
| concurrency-limits | Low | 3 | **0** | Added workflow `concurrency:` groups (`copilot-pricing-review`, `podcaster-handoff-smoke`, `trigger-podcast`) |
| undocumented-permissions | Low | 14 | 12 | Documented the scoped write perms that were fixed; remainder are explanatory-comment nits in `crawl-and-publish.yml`, `deploy-site.yml`, `security-scanning.yml`, `checkov.yml` |
| anonymous-definition | Informational | 15 | 15 | Deferred — naming jobs in large generated/complex workflows; no security impact |

All **High** findings are resolved. The default (`regular`) persona that CI
enforces reports **no findings**, so the Phase-C blocking flip is safe.

### Deferred (pedantic info/low, no CI impact)

- `undocumented-permissions` (Low ×12) — add explanatory comments next to
  remaining `permissions:` blocks.
- `anonymous-definition` (Informational ×15) — add `name:` to jobs in
  `crawl-and-publish.yml` and peers.

These are documentation/hardening nits surfaced only by `--persona pedantic`;
they do not affect the default-persona CI gate.

## Running locally

```bash
# Install (matches the action's toolchain family)
pipx install zizmor      # or: pip install zizmor

# Default persona (what CI reports)
zizmor .github/workflows/

# Deeper audit used to build the Phase-B backlog
zizmor --persona pedantic .github/workflows/

# Mirror the CI input set (exclude generated Squad workflows)
zizmor $(find .github/workflows -maxdepth 1 -type f \
  \( -name "*.yml" -o -name "*.yaml" \) \
  ! -name "squad-*.yml" ! -name "sync-squad-labels.yml" | sort)
```

## Phase plan

- **Phase A:** confirm non-blocking + SARIF wiring; record baseline. ✅
- **Phase B:** fix High-severity excessive-permissions + concurrency-limits. ✅ (info/low nits deferred above)
- **Phase C:** blocking enforcement (#545). ✅ Dropped `continue-on-error` on the
  `zizmor-scan` job; default-persona findings now fail the build. Mark it required.
