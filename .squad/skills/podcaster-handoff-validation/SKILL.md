---
name: podcaster-handoff-validation
description: Validate Podcaster handoff without exposing secrets or publishing content
domain: quality, pipeline-validation, secret-handling
confidence: medium
source: Fry Podcaster handoff QA validation
---

## Pattern

- Gate post-publish handoffs on the exact eligible mode (`run_mode == "normal"`) and on successful upstream publish/deploy jobs; broad negative filters are easy to miss when new rerun modes are added.
- Keep downstream handoff failures non-blocking and outside the article publication success criteria; warn and preserve the completed publish.
- Validate the publish manifest immediately before handoff so no-AI, stale, failed, or unpromoted candidates cannot leak into downstream generation.
- Validate client behavior locally with a localhost mock server and a placeholder API key.
- Check secret availability by presence only; never print or retrieve secret values.
- Use project-local scratch space via `TMPDIR=$PWD/.copilot/local-tmp` so existing tests that call `tempfile` do not write outside the repo.
- Treat workflow dry-run support as valid only if the Podcaster job actually runs and sends `dry_run: true` without publishing or mutating production content.

## Anti-patterns

- Dispatching a normal publish workflow solely to test a downstream handoff.
- Reading `.env` or printing configured secret values for validation.
- Assuming a pipeline `dry-run` validates handoff when the handoff job is skipped by workflow conditions.
