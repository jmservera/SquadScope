---
updated_at: 2026-06-26T20:59:59Z
phase: Production — Pipeline mature, hardening DevSecOps
focus_area: Security Guardrails & CI Enforcement
active_issues: [540, 541, 542, 543, 544, 545, 546]
---

# What We're Focused On

**Pipeline is in production.** Weekly/monthly/yearly trend analysis ships with SEO, month/year synthesis, and Podcaster handoff all live.

**Current thrust: DevSecOps guardrails** — staged rollout of linting and security gates without breaking the publish pipeline.

## Active Workstream — Security Guardrails (#540–#546)
- **Phase A (baselines, warning-only):** Ruff Python lint (#540), Checkov IaC/container (#541), Zizmor Actions security (#542)
- **Phase B:** Fix existing ruff/checkov/zizmor violations (#543)
- **Phase C (enforcement):** CI gates in blocking mode (#545), pre-commit/pre-push hooks (#544)
- **DevSecOps agent:** New specialist + copilot-instructions guardrail rules (#546)

## Standing Constraints
- ⛔ Never bypass branch rulesets — all changes via feature branch + PR (operator directive, 2026-06-13)
- 🤝 `config/podcast.json` and `scripts/podcaster_handoff.py` changes must coordinate with SquadScope-Podcaster
- ✅ CI must be correct, not just green — never weaken tests/gates to pass
