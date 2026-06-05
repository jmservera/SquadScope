# Fry QA triage decision

Date: 2026-06-05T15:36:19.379+00:00

## Decision

The crawl-and-publish analysis stage should degrade to a data-only no-AI weekly summary when both Copilot output and GitHub Models output are unavailable or rejected by the quality gate.

## Rationale

A missing or unauthorized model is an operational dependency failure, but the pipeline still has verified crawl data. Publishing a clearly labeled data-only summary is more reliable than failing the entire weekly handoff after preserving no reader-facing output.

## Follow-up

If model access is restored, the AI analysis path remains preferred. The no-AI path is only a terminal fallback after Copilot and GitHub Models fail.
