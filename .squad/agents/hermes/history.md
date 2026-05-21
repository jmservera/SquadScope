# Hermes — History

## Core Context
- Owns security review for application code, dependencies, and CI workflow changes.
- Evaluates risk with the full pipeline in mind, not just single-file diffs.

## Learnings
- Branch protection must stay intact; automation should use the shared `branch-protection-pr-workflow` skill instead of bypasses.
- The current pipeline chains GitHub crawl data, press correlation, AI analysis, content generation, and GitHub Pages deployment, so security review must cover every handoff.
- The safest fallback posture is Copilot CLI first, GitHub Models second, and a bounded no-AI summary path after that.
- Retry logic and prompt sanitation both matter for defense-in-depth when external content can influence analysis prompts.
