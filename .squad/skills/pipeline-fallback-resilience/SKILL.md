---
name: "pipeline-fallback-resilience"
description: "Keep multi-stage publishing workflows productive when optional AI services are unavailable."
domain: "quality"
confidence: "high"
source: "Fry triage of crawl-and-publish analyze failure"
date: "2026-06-05T15:36:19.379+00:00"
---

## Context

Weekly publishing should not fail entirely when an optional AI analysis provider is unavailable, unauthorized, or returns output rejected by quality gates. If crawl data is valid, the pipeline can still publish a clearly labeled data-only artifact.

## Patterns

- Treat model access errors as real pipeline reliability bugs, not transient noise, when they block publication.
- Keep AI output on the preferred path, but add a terminal deterministic fallback that uses already-validated data.
- Run the same quality gate against fallback artifacts so degraded output remains structurally publishable.
- Record the fallback source and model explicitly, such as `source=no-ai` and `model=none`, for later metrics review.

## Anti-Patterns

- Letting an external AI provider outage erase an otherwise valid weekly crawl.
- Bypassing quality gates for fallback output.
- Hiding degraded output as if it were full editorial analysis.
