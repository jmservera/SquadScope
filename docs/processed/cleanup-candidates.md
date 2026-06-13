# Cleanup Candidates (Archived 2026-06-13)

> **Status:** All actionable items resolved. Archived to `docs/processed/`.
> Scripts archived via PR #461; legacy data files removed; branding updated via PR #450/#374; `budget_alerts.py` wired into CI via PR #455; rollout-checklist corrected.

This was a conservative cleanup pass focused on `scripts/`, `docs/`, `data/`, and tracked root-level files.

## Findings

| Path | Reason | Recommendation |
| --- | --- | --- |
| `scripts/calibrate_hype_risk.py` | No workflow, doc, test, or script references were found. It appears to be an unwired experiment rather than an active pipeline component. | **Archive or delete** unless there is a near-term plan to wire it into the learning loop. |
| `scripts/momentum_tracker.py` | No workflow or docs references were found, and it does not appear to be called by the weekly pipeline. It looks like a standalone learning-loop utility that never got integrated. | **Archive or document/wire up**; if the momentum loop is deferred, move it out of the active script surface. |
| `scripts/budget_alerts.py` | Only test coverage references were found; no workflow or operator documentation calls it. Current cost tracking appears to stop at ledger generation. | **Wire into CI or archive** to reduce dormant maintenance surface. |
| `scripts/hindsight_validation.py` | Only test references were found; no workflow or docs integration was found for scheduled hindsight validation. | **Archive or add an owning workflow/doc** if hindsight validation is still part of the roadmap. |
| `scripts/init_topic_learning.py` | Only test references were found, with no workflow or operator-guide usage. Topic learning state currently looks pre-seeded in-repo rather than initialized through this command. | **Archive or document** as a manual bootstrap tool. |
| `data/raw/2026-W21-techcrunch.json` | Legacy raw artifact format. The current pipeline writes `YYYY-WNN-external-news.json` and only keeps `*-techcrunch.json` as a compatibility fallback. | **Archive or delete** once the legacy fallback is removed. |
| `data/raw/2026-W22-techcrunch.json` | Same issue as above: legacy TechCrunch-only artifact retained after the canonical external-news merge format was introduced. | **Archive or delete** once fallback support is no longer needed. |
| `docs/rollout-checklist.md` | The optional verification section still says a Copilot outage should fall back to GitHub Models, but the current repo explicitly documents that there is **no** GitHub Models/OpenAI fallback for weekly analysis. | **Update** to match the current fail-closed Copilot-only pipeline. |
| `docs/processed/qa-report.md` | This report says the deploy workflow does not build Pagefind and that reskill is still a placeholder. Both statements are stale relative to the current workflow. | **Archive or mark obsolete** so readers do not treat it as current operational truth. |
| `docs/processed/learning-audit.md` | The audit says there is no reskill job, no `.squad/skills/` directory, and no run-counter support. Those claims no longer match the repository shape or workflow wiring. | **Archive or add a superseded banner**. |
| `docs/processed/PRD-techcrunch-integration-2026-05-cross-source-correlation.md` | This PRD still describes `data/raw/YYYY-WNN-techcrunch.json` as the new primary artifact, but the implemented pipeline now uses `YYYY-WNN-external-news.json`. | **Archive or annotate as superseded** by the merged external-news design. |
| `docs/growth/distribution-strategy.md` | The document still points to `https://jmservera.github.io/SquadScope/` and related RSS URLs instead of the current Claracle domain. | **Update** branding and canonical URLs to `https://www.claracle.com/`. |
| `README.md` | The root README still advertises the old GitHub Pages URLs rather than the public Claracle domain. | **Update** to align external-facing docs with the live brand/domain. |

## Notes

- **Unused config files:** none clearly identified. `config/podcast.json` and `config/external_news_sources.json` are both referenced by workflows/scripts.
- **Empty or stub files:** no actionable tracked candidates found in the requested areas. `.gitkeep` placeholders and `scripts/__init__.py` appear intentional.
