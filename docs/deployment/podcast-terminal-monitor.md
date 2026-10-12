# Podcast terminal monitoring

Real generation remains behind the `podcaster-real-generation` environment's
required approval and main-only branch policy. Do not remove those controls
to validate configuration, and do not redispatch a publication that already
has an accepted receipt.

## Configure before generation

Set `PODCASTER_ENDPOINT`, `PODCASTER_STATUS_ENDPOINT`, and the
`PODCASTER_API_KEY` secret in that environment. Both automatic and manual
generation validate the status URL before calling generation. Automatic
dispatch validates before the mutation receipt boundary as well. A missing
or invalid URL fails clearly before admission, rather than accepting a job
that cannot be monitored. HTTPS is required except for local loopback tests;
embedded URL credentials and fragments are rejected. This is a configuration
preflight, not a proof that the deployed adapter is healthy.

The status adapter must implement `podcast_publication_status_v1`:

- Authenticated GET using `x-podcaster-api-key`.
- Query parameters: `week`, `publish_run_id`, `article_sha256`,
  `manifest_sha256`, `job_id`, and `correlation_id`.
- Response repeats the exact `identity`, `job_id`, and `correlation_id`.
- `synthesis.state`: `pending`, `started`, `succeeded`, `failed`, or `unknown`.
- `video.state`: `pending`, `succeeded`, `failed`, or `unknown`.
- `provider.state`: `pending`, `published`, `failed`, or `unknown`;
  `provider.external_verified` is a boolean.

The adapter owns provider readback against configured publication policy.
Processed **unlisted** YouTube and published Spotify can be verified success;
public YouTube is not a consumer requirement. Admission, a video artifact,
or an unverified provider write is never terminal success. Schema, identity,
and correlation mismatch fail closed; credentials and response bodies must
not appear in incidents or logs.

## Acceptance-relative budget

The deployed ACA limits checked on 2026-10-12 are 1,800 seconds for synthesis
and 5,400 seconds for video editing/distribution. Recorder jobs run within the
video fan-in window (900 seconds each), not an additional sequential stage.
The terminal evidence window is **7,800 seconds / 130 minutes**: the two
sequential replica budgets plus a bounded 600-second combined queue/startup
allowance. It starts at the accepted receipt timestamp, not workflow creation,
approval, or reconciliation startup. A restart or delayed reconciliation does
not reset that window. The existing synthesis-start warning at 600 seconds
remains a warning, not an early terminal deadline.

The monitor reserves **120 seconds** beyond evidence collection for receipts
and incident cleanup (7,920 seconds total). The reconciliation job has a
**135-minute** limit, allowing another three minutes for checkout, artifact
download, and bounded ledger resolution; it stays below GitHub's six-hour job
limit. Preserve the bounded request/error budgets. Do not turn exhaustion into
success, extend the window on every poll, or automatically retry generation.

W41 took 80 minutes 16 seconds from acceptance to publication, so the former
58-minute evidence deadline was incorrect even for known successful traffic.
If the real deadline expires, persist the stage-specific timeout and reconcile
the existing job's authoritative status before considering any new request.
W42 (`podcast-2026-W42-84c67c525182`) is already published and must not be used
as a duplicate-generation smoke test.

## Safe verification

Run the dispatch-state, handoff, and workflow contract tests and the pinned
Ruff, Checkov, and Zizmor gates. Independently verify the deployed status adapter
with an **existing accepted identity**, using protected authentication without
logging its key. A URL preflight passing is insufficient rollout evidence:
the adapter and environment variable must both be deployed/configured before
next week's protected approval. No production generation is needed to validate
these changes.
