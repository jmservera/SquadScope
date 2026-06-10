### 2026-06-10T10:27:49.647+00:00: Tick / Checklist
**By:** squadscope (automated)
**What:**
- Confirm and document the Podcaster HTTP API contract (request fields plus the response schema, e.g. the proposed Podcaster-side `job_id`, `status`, and `errors` fields) once Podcaster attaches it
- Confirm the authentication header name and the canonical secret name used to store the Podcaster API key (Podcaster-side proposal: `PODCASTER_API_KEY`)
- Document accepted status values and retry semantics for non-2xx responses
- Confirm and document the canonical publish manifest field names (e.g. reconcile freshness status and artifact URL fields; proposed Podcaster-side names `freshness_status` vs `freshness`, `artifact_url` vs `url`)
- Provide example request/response JSON and canonical endpoint URL(s)
- Confirm dry-run semantics and non-blocking handoff behavior

**Next steps:**
1. Author or attach a concise API contract doc (e.g. `docs/integration-contract.md`) with request/response schemas and examples; treat the field names above as Podcaster-side proposals until the contract is attached.
2. Update pipeline docs to reference the API contract and confirm/document the canonical Actions secret names (Podcaster-side proposal: `PODCASTER_ENDPOINT`, `PODCASTER_API_KEY`).
3. Add integration smoke test instructions and an operator checklist for manual runs.
