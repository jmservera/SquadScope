# Plan: podcast-auto-dispatch

**Date:** 2026-09-08  
**Status:** Approved — "go ahead" from jmservera  
**PRD:** jmservera/SquadScope PR #743 (docs/prds/podcaster-auto-dispatch.md)  
**Worktree:** /home/azureuser/source/SquadScope-auto-dispatch  
**Branch:** feat/podcast-auto-dispatch  

## Context

Implement automatic podcast dispatch after weekly article merges to main. W37 already dispatched manually — implementation must not re-dispatch it. Key decisions recorded in `.squad/decisions/inbox/bender-podcast-auto-dispatch-decisions.md`.

Trusted correlation: `push` to main → `content/weekly/**/*.md` path filter → SHA256 match against manifest on `origin/publish`. Duplicate prevention: concurrency group + GitHub API check + Podcaster idempotency.

## Phases

### P01 — Detection script [ ]
- [ ] P01-T01: Create `scripts/auto_dispatch_detect.py`
  - Accepts: article_path, before_sha, current_sha (or explicit week override for manual)
  - Fetches origin/publish
  - Scans `data/candidates/<week>/*/publish-manifest.json` for SHA256 match
  - Returns: week, run_id, manifest_path, article_sha256, eligible (bool), reason
  - Fails closed: missing/ambiguous/mismatched evidence → eligible=false
  - Respects `PODCAST_AUTO_DISPATCH_PAUSED` env var
  - No untrusted text used for logic
- [ ] P01-T02: Add duplicate-check helper
  - Uses GitHub API to list recent trigger-podcast.yml and auto-podcast-dispatch.yml successful runs
  - Checks for same week+run_id before proceeding

### P02 — Workflow: auto-podcast-dispatch.yml [ ]
- [ ] P02-T01: Create `.github/workflows/auto-podcast-dispatch.yml`
  - Trigger: `push` to `main`, paths: `content/weekly/**/*.md`
  - Also: `workflow_dispatch` with `observe_only` boolean input (rollout step 3)
  - Concurrency: `podcast-auto-dispatch-{{ week }}-{{ run_id }}` (set dynamically from detect outputs)
  - Job 1 `detect`: runs scripts/auto_dispatch_detect.py, outputs week/run_id/eligible
  - Job 2 `real-generation`: depends on detect, if: eligible && !observe_only
    - environment: podcaster-real-generation (keeps human approval gate)
    - Validates manifest + article (same steps as trigger-podcast.yml)
    - Calls scripts/podcaster_handoff.py --require-merged
    - Retains evidence in step summary (same as trigger-podcast.yml)
  - Permissions: contents: read; actions: read (for dedup check)
  - Protections: only runs from main (not forks/PRs), exact SHA-based checkout
  - zizmor/checkov compliance: annotations for intentional patterns
- [ ] P02-T02: Add observe-only job summary
  - When observe_only=true: records which dispatch WOULD have been created, no Podcaster call
- [ ] P02-T03: Add operational alert step
  - On eligible-but-paused: comment on weekly tracking issue
  - On detect failure: annotate job summary

### P03 — Tests [ ]
- [ ] P03-T01: Create `tests/test_auto_dispatch_detect.py`
  - Happy path: new article → matching manifest → eligible=true
  - No matching manifest → eligible=false
  - SHA256 mismatch → eligible=false
  - Multiple candidates same week → selects correct one by SHA256
  - Ineligible manifest (publish_eligible=false) → eligible=false
  - Article not newly added (diff-filter) → eligible=false
  - PODCAST_AUTO_DISPATCH_PAUSED=true → deferred result
  - Week format validation
  - Invalid/malformed manifest → eligible=false (fail closed)
- [ ] P03-T02: Add fixtures (minimal manifest JSON, mock article content)
- [ ] P03-T03: Run existing test suite; confirm no regressions

### P04 — Security/pipeline reviews [ ]
- [ ] P04-T01: URL review — workflow permissions, actions versions, zizmor, checkov
- [ ] P04-T02: Hermes review — threat model, fork safety, injection, secret scope
- [ ] P04-T03: Address review findings

### P05 — PR, CI, release [ ]
- [ ] P05-T01: Push branch feat/podcast-auto-dispatch
- [ ] P05-T02: Open PR with evidence summary
- [ ] P05-T03: Leela code review
- [ ] P05-T04: CI passes (existing gates respected)
- [ ] P05-T05: Merge

## Out of scope / follow-up

- Rollout steps 5-6 (four-consecutive verification, remove observe-only instrumentation)
- Cross-repo contract changes (coordinate with coordinator before expanding)
- W37 auto-dispatch (W37 already dispatched — dedup prevents re-trigger)
