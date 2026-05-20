# Leela — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** TBD (GitHub Actions for automation, static site for GitHub Pages)
- **User:** jmservera
- **Goal:** Review new GitHub repos weekly, track trending repos by stars, summarize trends with critical thinking about what's important, what's trending, and what's missing. Future expansion to other tech news platforms.

## Learnings

### 2026-05-19T18:05:10+02:00 — CI Workflow: PR-based commits, ruleset bypass reverted

- **Ruleset fix:** Removed RepositoryRole:5 bypass actor from the `main` ruleset (id 16532660). Branch protection must never be bypassed.
- **Workflow refactor:** All commit steps in `crawl-and-publish.yml` now create a timestamped branch, open a PR via `gh pr create`, and auto-merge with `--squash --auto` instead of pushing directly to main.
- **Steps renamed:** "Commit crawl data" → "Commit crawl data via PR", "Commit analysis" → "Commit analysis via PR", "Commit generated content" → "Commit generated content via PR", reskill step also converted.
- **No more `continue-on-error: true`** on commit steps — they succeed properly now via the PR path.
- **Tests updated:** Adjusted step name references in `tests/test_pipeline.py` to match new naming.
- **Decision recorded:** `.squad/decisions.md`

### 2026-05-19T22:57:55+02:00 — CI Self-Learning Pipeline Architecture

- **Deliverable:** `.github/agents/farnsworth.agent.md` — dedicated CI agent file with learning loop instructions
- **Architecture decisions:**
  - Copilot CLI `--agent` flag loads Farnsworth identity in both analysis and reskill jobs
  - Post-analysis learnings committed atomically with analysis data to `publish` branch
  - Reskill promoted to Copilot CLI primary path (was GitHub Models only); agent can now update wisdom.md directly
  - Default model switched from `openai/gpt-4.1` (403) to `openai/gpt-4o` across all fallback paths
- **Key insight:** The learning loop requires three properties: (1) identity loaded before work, (2) state persisted after work, (3) persisted state injected into next run. The agent file provides (1), the commit step provides (2), and the existing prompt templates with `{{WISDOM}}`/`{{SKILLS}}` provide (3).
- **Decision recorded:** `.squad/decisions.md`
- **Files modified:** `crawl-and-publish.yml` (analysis + reskill steps), `scripts/reskill.py`, `scripts/analyze_fallback.py`

### 2026-05-19T20:57:55Z — Scribe Archival & Team Sync

- **Scribe executed full archival cycle:** decisions.md merged 4 inbox files (Farnsworth correlations narrative, divergence narrative, no-AI re-render; Leela CI self-learning), cleared inbox, created orchestration logs for both agents, recorded session log, updated both agent histories.
- **Decisions now in permanent log:** All three Farnsworth polish decisions + Leela self-learning architecture decision moved to `.squad/decisions.md` main document.
- **Orchestration recorded:** `.squad/orchestration-log/2026-05-19T20:57:55Z-{farnsworth,leela}.md` — outcomes linked to PR #139 and #140.
- **Status:** Team sync complete. Ready for next cycle.

### 2026-05-19T23:25:32+02:00 — Fix: Copilot CLI --agent flag takes name, not path

- **Bug:** PR #140 shipped `--agent .github/agents/farnsworth.agent.md` but the CLI expects the agent **name** from YAML frontmatter (`name: Farnsworth`), not a file path. CI error: `No such agent: .github/agents/farnsworth.agent.md, available: Farnsworth, Squad`.
- **Fix:** Changed to `--agent Farnsworth` in both analysis and reskill jobs. Simplified `-p` prompts to minimal file-read instructions since the agent file already contains full identity/instructions.
- **Key learning:** Copilot CLI auto-discovers `.github/agents/*.agent.md` files and registers them by their frontmatter `name:` field. Always reference agents by name, never by path.
- **PR:** #141 (squash-merged to main). Pipeline re-triggered.
- **Tests:** All 519 passed.
