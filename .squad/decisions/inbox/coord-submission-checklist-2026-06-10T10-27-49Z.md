### 2026-06-10T10:27:49.647+00:00: Tick / Checklist
**By:** squadscope (automated)
**What:**
- Verify Podcaster HTTP API contract (request fields, response schema: job_id, status, errors)
- Confirm authentication header name and allowed secret storage (PODCASTER_API_KEY usage)
- Document accepted status values and retry semantics for non-2xx responses
- Normalize publish manifest field names (freshness_status vs freshness, artifact_url vs url)
- Provide example request/response JSON and canonical endpoint URL(s)
- Confirm dry_run semantics and non-blocking handoff behavior

**Next steps:**
1. Author or attach a concise API contract doc (podcaster-api.md) with request/response schemas and examples.
2. Update pipeline docs to reference the API contract and required Actions secret names (PODCASTER_ENDPOINT, PODCASTER_API_KEY).
3. Add integration smoke test instructions and an operator checklist for manual runs.
