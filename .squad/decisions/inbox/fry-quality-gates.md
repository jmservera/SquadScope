# Fry: quality gate fallback hardening

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.
