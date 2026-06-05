# Bender PR #236 Security Fix

## Context
Hermes blocked PR #236 because config-driven external RSS sources were fetched directly without egress URL validation or explicit per-request timeouts.

## Decision
External news RSS source configs now require HTTPS URLs whose host is in the approved feed allowlist, with credentials, local/private/link-local targets, and unexpected ports rejected before crawl. Fetching now goes through `urllib.request.urlopen` with an explicit bounded timeout before handing bytes to `feedparser`, while retaining the existing config-driven source list and bounded in-process worker pool.

## Validation
Added tests for invalid/unapproved URL rejection and explicit fetch timeout propagation. Ran `PYTHONPATH=. .venv/bin/python -m pytest tests -q` with 563 passing tests.
