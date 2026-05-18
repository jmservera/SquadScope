# Bender crawler hardening note

- **Date:** 2026-05-18T10:59:10.800+02:00
- **Context:** Issue #6 crawler hardening
- **Decision to review:** Treat README lookups as a degradable signal instead of a hard-stop path. The crawler now caches API responses, saves weekly star snapshots under `data/snapshots/`, logs rate-limit state, and caps README retry delays so partial failures are recorded in metadata instead of blocking the full weekly crawl.
- **Why it matters:** Search queries are cheap, but hundreds of README checks can trigger secondary throttling. Bounded retries plus persistent cache keep Phase 1 crawls finishable and give Farnsworth usable JSON even when GitHub responses are partial.
