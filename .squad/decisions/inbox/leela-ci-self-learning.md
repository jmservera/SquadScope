# Decision: CI Self-Learning Pipeline Architecture

**Date:** 2026-05-19T22:57:55+02:00
**Author:** Leela (Lead/Architect)
**Status:** Proposed
**Scope:** Analysis and reskill CI jobs — self-learning loop

## Context

The CI pipeline runs AI analysis (Copilot CLI) and reskill (GitHub Models API) but neither job leverages the squad agent system. The analysis agent has no identity, cannot read its own history/skills, and has no mechanism to write learnings back. The reskill job bypasses Copilot CLI entirely and uses a model (`openai/gpt-4.1`) that returns 403.

## Decisions

### 1. Dedicated Farnsworth Agent File (`.github/agents/farnsworth.agent.md`)

A standalone agent file gives the Copilot CLI the full Farnsworth identity — charter, history reading instructions, post-analysis learning format, and write permissions to `.squad/`.

**Rationale:** The `--agent` flag loads an agent markdown file with YAML frontmatter and instructions. A dedicated file allows CI-specific directives (learning output format, file write permissions) without polluting the interactive Squad coordinator agent.

### 2. `--agent` Flag in Copilot CLI Invocations

Both the analysis and reskill jobs now use:
```bash
copilot --agent .github/agents/farnsworth.agent.md ...
```

**Rationale:** This loads Farnsworth's identity, making the CLI aware of the agent's history, wisdom, skills, and learning expectations.

### 3. Learning Commit Strategy: Same Branch, Same Job

After analysis, `.squad/` changes (history, skills) are committed alongside `data/analyzed/` to the `publish` data branch in a single atomic commit.

**Rationale:** No additional branch/PR overhead. The data branch is unprotected and already receives CI commits. Learnings are part of the analysis artifact — they should be co-located temporally. The reskill job already commits `.squad/` state via the same pattern.

### 4. Model Fallback: `openai/gpt-4o` Replaces `openai/gpt-4.1`

The default model for GitHub Models API fallback is changed from `openai/gpt-4.1` (which returns 403) to `openai/gpt-4o` (widely accessible).

**Rationale:** `gpt-4.1` is not accessible via the GitHub Models API for this repository's token. `gpt-4o` is the current generally available model. The env var `GITHUB_MODELS_MODEL` still allows override.

### 5. Reskill Primary Path: Copilot CLI with Agent

The reskill job now tries Copilot CLI first (with agent identity), falling back to GitHub Models API if CLI is unavailable. This gives reskill the same agent-aware capabilities as analysis: read wisdom/skills/history, write updated wisdom and learnings back.

**Rationale:** The reskill cycle is the primary mechanism for reinforcing the learning loop. With agent identity, it can directly update `wisdom.md` and `history.md` based on retrospective findings — the core of self-improvement.

### 6. Prompt Template Unchanged

The existing prompt templates (`prompts/analyze-weekly.md`, `prompts/reskill.md`) already inject wisdom and skills via `{{WISDOM}}` and `{{SKILLS}}` placeholders. The agent file complements this by providing identity context and learning output instructions that the templates alone cannot express.

## Risks

| Risk | Mitigation |
|------|-----------|
| Agent writes bad content to `.squad/` files | Quality gate still runs on analysis output; .squad changes are append-only learnings |
| Copilot CLI doesn't support `--agent` as expected | Fallback path (GitHub Models via reskill.py) still works without agent identity |
| Learning state diverges between publish branch and main | Periodic sync PRs already exist; learnings on publish are forward-compatible |

## Implementation

- [x] `.github/agents/farnsworth.agent.md` — agent identity file
- [x] `.github/workflows/crawl-and-publish.yml` — `--agent` flag, learning commits, model fix
- [x] `scripts/reskill.py` — model default updated to `openai/gpt-4o`
- [x] `scripts/analyze_fallback.py` — model default updated to `openai/gpt-4o`
