# Prompt Injection Hardening for Analysis Prompts

**Date:** 2026-05-25
**Author:** Hermes
**Status:** Proposed

## Context

Nibbler's RAI audit identified user-controlled GitHub repository descriptions entering the weekly analysis prompt through `{{RAW_JSON_CONTENT}}`. A malicious repo description can contain prompt-injection text that attempts to override Farnsworth's editorial instructions.

## Decision

Apply a layered OWASP LLM01 defense for analyzer prompt rendering:

1. Mark raw crawl JSON as untrusted data with explicit `<untrusted-content>` boundaries.
2. Sanitize repository descriptions before prompt rendering by stripping leading whitespace, escaping boundary-closing tags, truncating long text, and warning on common prompt-injection phrases.
3. Add output guardrails telling the analyst to stop on unsupported claims and avoid verbatim descriptions containing meta-instructions.
4. Repeat the editorial mission after the untrusted content so late prompt text reinforces trusted instructions.

## Consequences

The analyzer keeps using the same editorial structure, but prompt provenance is clearer and repository descriptions have bounded influence. Suspicious descriptions are logged and truncated rather than blocked to avoid false positives disrupting publication.
