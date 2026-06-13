# AI Agents

This repository is managed by an AI Squad team. The default agent for all work is **Squad**.

## Usage

```bash
# Default: use Squad agent for all tasks
copilot --agent squad -p "your task here" --allow-all-tools

# For automated issue work (Ralph loop)
squad triage --execute --interval 20 --copilot-flags "--allow-all-tools"
```

## Team Roster

See `.squad/team.md` for the full team composition. Key members:

- **Leela** — Lead (architecture, code review, triage)
- **Bender** — Crawler (data pipeline, GitHub API)
- **Farnsworth** — Analyst (content generation, AI analysis)
- **Amy** — Frontend (Hugo templates, CSS, UX)
- **Fry** — Tester (pytest, quality gates)

## Related Repositories

- [SquadScope-Podcaster](https://github.com/jmservera/SquadScope-Podcaster) — Podcast generation engine (consumes `config/podcast.json`)
- [SquadScope-Coordinator](https://github.com/jmservera/SquadScope-Coordinator) — Orchestration layer
