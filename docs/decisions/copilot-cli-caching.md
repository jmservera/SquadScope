# Copilot CLI Caching Investigation

## Status: No Explicit Cache Support Available

**Date:** 2026-05-21
**Author:** Amy & Fry (SquadScope Squad)

## Current Status

### Copilot CLI (Primary Path)

- Copilot CLI in CI mode does **NOT** support explicit prompt caching
- No flags or configuration options exist to enable cache reuse between runs
- Each invocation sends the full prompt context to the model
- GitHub has not announced any roadmap for prompt caching in the CLI

### GitHub Models API (Fallback Path)

- The GitHub Models API also does **NOT** expose cache control headers or parameters
- Token usage is billed per-request with no discount for repeated prefixes
- No mechanism to pin or reuse cached prompt segments

### Anthropic API (Direct Access)

- Anthropic's API **does** support prompt caching via `cache_control` blocks
- Cached input tokens are billed at $0.30/1M instead of $3.00/1M (for Claude Sonnet 4)
- Cache has a 5-minute TTL with automatic extension on cache hits
- Requires direct API access (not available through Copilot CLI or GitHub Models)

## Cost Impact Analysis

| Scenario | Input Token Cost | Savings |
|----------|-----------------|---------|
| No caching (current) | $3.00/1M tokens | — |
| With Anthropic caching | $0.30/1M tokens (cached) | ~77% reduction |
| Typical weekly run (~80K tokens) | $0.24 → $0.056 | ~$0.18/run saved |

For our current usage (~3 runs/week), potential monthly savings: ~$2.16

## Recommendation

1. **Short-term:** Continue using Copilot CLI as primary path. The convenience and integration benefits outweigh the caching cost savings at our current volume.

2. **Medium-term:** Monitor GitHub's announcements for:
   - Prompt caching support in Copilot CLI
   - Cache-aware billing in GitHub Models API
   - Any new `--cache` or `--session` flags

3. **Long-term / High-volume:** If SquadScope scales to daily runs or multi-org deployments, consider switching to direct Anthropic API access to leverage prompt caching. This becomes worthwhile when:
   - Monthly token volume exceeds 1M input tokens
   - The same system prompt is reused across multiple runs within 5 minutes
   - Cost savings justify the added complexity of API key management

## References

- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [GitHub Copilot CLI Documentation](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line)
- [GitHub Models API](https://docs.github.com/en/github-models)
