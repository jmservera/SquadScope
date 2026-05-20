# 2026-05-20: Prevent Copilot stdout from leaking into published markdown

- **Owner:** Farnsworth
- **Date:** 2026-05-20T22:14:02+02:00
- **Status:** Proposed
- **Decision:** In `crawl-and-publish.yml`, Copilot CLI stdout must never be redirected to the same markdown file that the agent writes via the `write` tool. Analysis and reskill invocations should send stdout to `/dev/null`, rely on `--share` or workflow logs for transcripts, and run a post-write sanitizer over the target markdown file as defense in depth.
- **Why:** The published week 21 article leaked agent status text because the shell appended Copilot CLI stdout to `data/analyzed/2026-W21-summary.md` after Farnsworth had already written the real article. The same collision pattern existed in the reskill path. Separating channels fixes the root cause, and a sanitizer reduces blast radius if the CLI emits metadata again.
- **Implementation notes:**
  - Changed both Copilot CLI redirects in `.github/workflows/crawl-and-publish.yml` from the output markdown file to `/dev/null`.
  - Added `scripts/sanitize_agent_output.py` and invoked it after analysis/reskill generation to strip leaked lines such as `✅ Farnsworth is done`, `Editorial thesis:`, and `Quality score:`.
  - Reinforced `prompts/analyze-weekly.md` so the agent writes only publication-ready markdown beginning with YAML frontmatter and ending with the final article line.
  - Left the quality gate reading `$OUTPUT_FILE`; it now validates the agent-written markdown only.
- **Scope:** `.github/workflows/crawl-and-publish.yml`, `prompts/analyze-weekly.md`, `scripts/sanitize_agent_output.py`, `tests/test_sanitize_agent_output.py`
