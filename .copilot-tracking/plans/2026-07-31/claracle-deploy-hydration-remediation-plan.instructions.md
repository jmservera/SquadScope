---
applyTo: '.copilot-tracking/changes/2026-07-31/claracle-deploy-hydration-remediation-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Deploy Hydration Remediation

## Overview

Resolve the production deploy failure introduced by PR #623 (issue #627), where the deploy hydrates `content/data/` from the `publish` branch that does not yet contain those pages, deleting the committed data pages that `content/embeds/` depends on and aborting the Hugo build. Ship an interim unblock, regenerate the observatory content onto `publish`, restore consistent hydration, and add a CI guard so this class of `main`/`publish` divergence fails CI rather than the deploy.

## Objectives

### User Requirements

* Take the "Path B" route: stop the deploy from hydrating `content/data/` so the committed pages ship until the crawl repopulates `publish` - Source: user request, 2026-07-31
* Run the crawl/generation actions to confirm the observatory data pages and chart embeds are generated onto `publish` - Source: user request, 2026-07-31
* Capture the incident, fix, and follow-up in the PRD and this plan for RPI handoff - Source: user request, 2026-07-31

### Derived Objectives

* Prevent a dangling `content/embeds/*` `source_page` from aborting the whole site build - Derived from: issue #627 build errors
* Make deploy and CI build the same hydrated content set so divergence is caught before production - Derived from: NFR-011 (PRD v1.2)
* Restore the "all generated content comes from publish" invariant once `publish` is populated - Derived from: deploy-site.yml architecture comment

## Context Summary

### Project Files

* `.github/workflows/deploy-site.yml` - "Hydrate generated content from publish" step; interim fix omits `content/data/`
* `.github/workflows/crawl-and-publish.yml` - canonical pipeline that generates observatory content and commits it to `publish`
* `.github/workflows/generate-data-pages.yml` - scheduled Observatory freshness check that hydrates the same paths
* `layouts/embeds/single.html` - `errorf` when an embed `source_page` is missing
* `layouts/shortcodes/observatory-chart.html` - `errorf` when the referenced data page is not found
* `content/embeds/fastest-growing-ai-repositories-chart/index.md` - hand-committed embed referencing `/data/fastest-growing-ai-repositories-this-year/`
* `content/data/` - observatory data pages committed on `main`, absent on `publish`
* `tests/test_pipeline.py` - `test_publish_transaction_carries_every_generated_path` provenance invariant

### References

* Issue #627 - deploy failure report (run 30616770243)
* `docs/prds/claracle-data-observatory-relaunch.md` v1.2 - NFR-011, NFR-012, R-08, Q-03
* `docs/data-observatory-runbook.md` - Observatory generation and publish operations
* `docs/design/data-observatory-model.md` - content/data provenance
* PR for #627 - interim Path B unblock (this plan's Phase 1)

### Standards References

* `.github/copilot-instructions.md` - testing, workflow security, and cross-repository conventions
* `.github/instructions/coding-standards/python-script.instructions.md` - Python requirements
* `.github/instructions/hve-core/markdown.instructions.md` - Markdown requirements

## Architecture Overview

```text
crawl-and-publish.yml (generate)         deploy-site.yml (build)
        |                                        |
        v                                        v
 generate observatory content            hydrate generated content
 (content/data, embeds deps)             from publish branch
        |                                        |
        v                                        v
 commit to publish branch  ----------->  build with hydrated content
        ^                                        |
        |                                        v
 CI deploy-parity build (new)            GitHub Pages deploy
 reproduces hydration + validates
 embed source_page references
```

## Affected Files Tree

```text
.github/workflows/
  deploy-site.yml
  crawl-and-publish.yml
  generate-data-pages.yml
  ci.yml
content/
  data/
  embeds/fastest-growing-ai-repositories-chart/index.md
layouts/
  embeds/single.html
  shortcodes/observatory-chart.html
scripts/
  (optional) check_embed_sources.py
tests/
  test_pipeline.py
docs/
  prds/claracle-data-observatory-relaunch.md
  data-observatory-runbook.md
```

## Design Patterns Applied

* Interim fail-safe: ship committed content until the generated source is ready
* Single source of truth for generated content on `publish`, restored after population
* Deploy/CI build parity so divergence fails CI, not production
* Build-time reference validation for embed `source_page`
* Least-change workflow edits with provenance-invariant test coverage

## Implementation Checklist

### [x] Implementation Phase 1: Interim Unblock (Path B)

<!-- parallelizable: false -->

* [x] Step 1.1: Omit `content/data/` from the deploy hydration list with an explanatory comment referencing issue #627
  * File: `.github/workflows/deploy-site.yml`
* [x] Step 1.2: Update the provenance invariant test so `content/data/` is verified through the crawl transaction but excluded from deploy hydration
  * File: `tests/test_pipeline.py`
* [x] Step 1.3: Validate locally: `pytest tests/test_pipeline.py`, zizmor on the workflow, and a clean `hugo --minify` build with the embed and its data page rendered

### [x] Implementation Phase 2: Regenerate Observatory Content onto Publish

<!-- parallelizable: false -->

* [x] Step 2.1: Trigger `crawl-and-publish.yml` (or the appropriate generation workflow) via `workflow_dispatch` and confirm the `generate` job commits `content/data/` and the chart-embed dependencies to `publish` — regenerated via crawl runs; `#634` stages only existing generated paths in the publish commit
* [x] Step 2.2: Confirm `git ls-tree -r --name-only origin/publish -- content/data/` lists `fastest-growing-ai-repositories-this-year/` and the other ranking pages
* [x] Step 2.3: Confirm the embed dependency resolves against the `publish` content set (the observatory-chart shortcode finds the data page)

### [x] Implementation Phase 3: Restore Consistent Deploy Hydration

<!-- parallelizable: false -->

* [x] Step 3.1: Re-add `content/data/` to the deploy hydration list and revert the interim comment once `publish` reliably carries the pages — restored via `#637` (generalize safe hydration guard and restore content/data deploy)
* [x] Step 3.2: Restore the provenance invariant test to require `content/data/` in deploy hydration — `#637`
* [x] Step 3.3: Confirm a full deploy build succeeds against the hydrated `publish` content set — deploy-site runs green since 2026-08-01

### [x] Implementation Phase 4: CI Deploy-Parity Guard

<!-- parallelizable: true -->

* [x] Step 4.1: Add a CI build that reproduces the deploy publish-hydration (or a lightweight check that every `content/embeds/*` `source_page` resolves to an existing data page in the built content set) — the lightweight `scripts/check_embed_sources.py` alternative shipped in `#641` and satisfies NFR-012; NFR-011 publish-hydration reproduction now ships as `scripts/publish_hydration.py` with the `publish-hydration-parity` CI job
* [x] Step 4.2: Wire the guard into the production-site job so `main`/`publish` divergence fails CI, not the deploy — the `publish-hydration-parity` job in `.github/workflows/ci.yml` hydrates the deploy's generated set from `publish` and validates the embed and promotion-record references before deploy
* [x] Step 4.3: Add or extend tests covering the guard behavior — `tests/test_embed_sources.py` (`#641`)

### [x] Implementation Phase 5: Validation and Re-Review

<!-- parallelizable: false -->

* [x] Step 5.1: Run full validation: `pytest tests/`, ruff, zizmor on changed workflows, and a clean Hugo build — validated per PR CI (`#628`/`#634`/`#637`/`#641`)
* [x] Step 5.2: Confirm the production deploy succeeds end to end and close issue #627 — `#627` CLOSED; deploy-site green
* [x] Step 5.3: Reconcile PRD NFR-011/012, R-08, and Q-03 status with the delivered state — reconciled 2026-08-07 in PRD 1.5: NFR-011/012 marked Delivered, R-08 and Q-03 closed on the `publish-hydration-parity` job, `scripts/publish_hydration.py`, and the `#641` embed-source guard

## Parallelization Summary

* Phase 1 is complete and sequential (interim unblock shipped in the #627 PR).
* Phase 2 must precede Phase 3 because deploy hydration can only be restored after `publish` carries the pages.
* Phase 4 can proceed in parallel with Phases 2 and 3 because the guard is independent of content population.
* Phase 5 is sequential and depends on all prior phases.

## Planning Log

* 2026-07-31: Root cause confirmed - PR #623 added `content/data/` to deploy hydration; `publish` (last updated 2026-07-27) lacks it, so `rm -rf` plus a failing `git checkout ... || true` empties the directory and the committed embed reference dangles. CI does not reproduce publish-hydration, so it stayed green. Interim Path B shipped.

## Dependencies

* Access to run `crawl-and-publish.yml` / generation workflows against `publish`
* Protected deploy environment and `publish` branch write access
* Hugo Extended 0.161.1 and pinned Python/Node tooling from CI
* URL ownership for deploy and CI workflow changes
* Bender ownership for observatory content generation

## Success Criteria

* The production deploy succeeds and issue #627 is closed - Traces to: issue #627
* `content/data/` and the chart embeds are generated onto `publish` by the crawl - Traces to: user request, deploy-site.yml architecture
* Deploy hydration is restored so generated content once again flows from `publish` - Traces to: NFR-011
* CI reproduces the deploy hydration (or validates embed `source_page` references) and fails on `main`/`publish` divergence - Traces to: NFR-011, NFR-012, R-08
* PRD NFR-011/012, R-08, and Q-03 reflect the delivered state - Traces to: PRD v1.2
