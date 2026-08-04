<!-- markdownlint-disable-file -->
# Claracle Podcaster Protection Research

## Research Questions

* What is the smallest safe workflow change that binds real, manually initiated Podcaster generation to a distinct GitHub environment?
* How can that change preserve dry-run smoke behavior, exact manifest selection, evidence retention, and the absence of automatic dispatch?
* Which controls belong in repository code, and which require GitHub environment policy or maintainer approval configuration?
* What exact files and tests should change?

## Findings

### Executive conclusion

The smallest safe design is a manual-only real-generation path with a separate
environment named `podcaster-real-generation`:

1. Bind `.github/workflows/trigger-podcast.yml` job `trigger-podcast` to
   `podcaster-real-generation`.
2. Make `publish_run_id` required and remove the latest-manifest fallback. Resolve
   only `data/candidates/${WEEK}/${PUBLISH_RUN_ID}/publish-manifest.json`.
3. Remove the real Podcaster handoff from
   `.github/workflows/sync-publish-to-main.yml`. The sync can remain automatic, but
   it must never call `scripts/podcaster_handoff.py` or read Podcaster credentials.
4. Leave `.github/workflows/podcaster-handoff-smoke.yml` and its deploy-site caller
   unchanged. That path remains a dry run, retains exact promotion evidence, and
   uses the distinct `podcaster-release-smoke` environment.
5. Emit safe structured outputs for the Podcaster `job_id` and accepted response
   status, then append an `if: always()` real-run summary. Do not include the API
   key, endpoint, breaking-news text, payload body, or response body in evidence.

An environment declaration is only a repository-side binding. GitHub documents
that running a job against a missing environment creates the environment without
protection rules or secrets. A repository administrator must therefore create and
protect `podcaster-real-generation` before the workflow change is exercised.

### Researched baseline

Research used current `main` revision
`4b7c5cf506b2e8b73350ff94ce80669c93810e66`. The workflow, script, and test sources
were unmodified in the worktree. The focused baseline passed:

```text
91 passed, 26 subtests passed in 6.75s
```

Command:

```bash
uv run --no-sync pytest -q \
  tests/test_pipeline.py \
  tests/test_podcaster_handoff.py \
  tests/test_sync_publish_workflow.py
```

### Current control paths

`.github/workflows/trigger-podcast.yml` is manually dispatched and sends a real
request, but its job has no environment. Its optional `publish_run_id` permits a
`find | sort -V | tail -1` fallback, so an operator can request a week without
pinning the exact manifest run.

`.github/workflows/sync-publish-to-main.yml` is automatically triggered after a
successful crawl-and-publish run. After merging generated content, it currently
calls the real Podcaster endpoint with `--require-merged`. This is an automatic
real-generation path and would bypass protection added only to the manual workflow.

`.github/workflows/podcaster-handoff-smoke.yml` is already isolated from real
generation:

* Its job uses `environment.name: podcaster-release-smoke`.
* It passes `--podcaster-dry-run` and `--exact-article-content`.
* It verifies the exact article digest, promotion transaction, source manifest
  digest, source manifest path, and publishing run before the network request.
* Its final step runs with `if: always()` and retains status, article path, article
  SHA-256, and Actions run URL in `GITHUB_STEP_SUMMARY`.
* `.github/workflows/deploy-site.yml` invokes this reusable smoke only after build
  and Pages deployment. This automatic dry run can remain because it does not
  generate an episode.

`scripts/podcaster_handoff.py` validates that a normal real manifest is eligible
and fails closed for malformed or ineligible manifests. It also validates that a
successful API response has status `accepted` or `dry_run` and a non-empty
`job_id`. It currently writes those values only to an Actions notice, not to
structured step outputs.

### Exact manifest and article safety

Making `publish_run_id` mandatory is the minimum deterministic selection control.
The locate step should additionally parse the selected JSON and fail unless:

* `manifest.week` equals the requested `week`.
* String-normalized `manifest.run_id` equals `publish_run_id`.
* The selected path is exactly
  `data/candidates/${WEEK}/${PUBLISH_RUN_ID}/publish-manifest.json`.

The real invocation should add `--require-merged` and remove the fallback that
checks the weekly article out from `origin/publish`. This preserves the safety
property lost when the automatic post-merge handoff is removed: generation can
only use article bytes already present on `main`, and those bytes must match the
selected manifest's `candidate.content_sha256`.

This is intentionally narrower than converting real generation to the smoke
workflow's promotion-transaction interface. Reusing exact-release mode currently
forces `dry_run: true` in `validate_exact_release_payload`; changing that contract
would enlarge the change and couple real generation to a mode designed for smoke.

### Evidence boundary

Repository code can retain the following in the real run summary:

* Workflow conclusion and `steps.handoff.outcome`
* Dispatcher (`github.actor`), which must not be mislabeled as the environment
  approver
* Requested week and required publish run ID
* Exact manifest path and manifest SHA-256
* Article path and verified article SHA-256
* Actions run URL
* Podcaster response `job_id` and response status

The Podcaster response status `accepted` proves request acceptance, not completed
episode generation. The Podcaster maintainer must use the retained `job_id` to
record the downstream final conclusion. GitHub's deployment review history or API,
not a workflow context, is the authoritative source for the environment approver.

### Repository code versus external policy

| Control | Repository implementation | GitHub or maintainer action |
| --- | --- | --- |
| Manual-only real entry point | Keep only `workflow_dispatch` in `trigger-podcast.yml`; remove real handoff from sync | Do not dispatch until authorization is recorded |
| Environment binding | Add `environment: { name: podcaster-real-generation }` to the real job | Admin creates and configures the environment before first run |
| Exact manifest | Require numeric `publish_run_id`; use one exact path; validate manifest week and run ID | Maintainer authorizes that exact week and run ID |
| Merged article identity | Use `--require-merged`; retain candidate/article digest | Maintainer confirms the selected episode is safe to create or rerun |
| Required review | No workflow YAML can define required reviewers | Admin selects reviewer(s) and enables prevent self-review |
| Branch restriction | Workflow can explicitly check out the default branch | Admin restricts deployment branches/tags to `main`; do not rely on `Protected branches only` if no branch rule exists |
| Bypass behavior | Not configurable in workflow YAML | Admin disables administrator bypass if repository policy permits |
| Credential scope | Job references `vars.PODCASTER_ENDPOINT` and `secrets.PODCASTER_API_KEY` only after environment admission | Admin stores the real endpoint/key on the real environment and URL reviews scope; use a distinct dry-run credential when supported |
| Approval evidence | Summary retains dispatcher and run URL | Deployment history retains approver; reviewer records dated decision |
| Downstream completion | Script retains accepted status and `job_id` | Podcaster maintainer verifies final job conclusion |

GitHub allows up to six required reviewers, but only one listed reviewer must
approve. Listing URL, Hermes, and a Podcaster maintainer does not enforce three
approvals. If all three approvals are required, retain two as procedural sign-offs
or implement a custom deployment protection rule; the standard environment reviewer
setting alone cannot express that policy.

## Recommendations

### Exact file changes

1. `.github/workflows/trigger-podcast.yml`

   * Change `publish_run_id.required` to `true` and describe it as the exact
     crawl-and-publish run ID.
   * Add `environment.name: podcaster-real-generation` to job `trigger-podcast`.
   * Explicitly check out `${{ github.event.repository.default_branch }}`.
   * Delete the latest-manifest fallback and always construct the exact candidate
     manifest path after numeric input validation.
   * Parse the manifest once to verify requested week/run ID and emit
     `manifest_path`, `manifest_sha256`, `article_sha256`, and `publish_run_id`.
   * Do not check the article out from `origin/publish`; require it on the default
     branch and pass `--require-merged`.
   * Give the real invocation `id: handoff`.
   * Add an `if: always()` summary step with the safe evidence fields listed above.

2. `.github/workflows/sync-publish-to-main.yml`

   * Delete `Set up Python` and `Trigger Podcaster after merge`.
   * Delete the `merged=true` output and comments that claim a later handoff will
     fire.
   * Keep content sync, PR creation, checks, and merge behavior unchanged.

3. `scripts/podcaster_handoff.py`

   * After successful response validation, append escaped `podcaster_job_id` and
     `podcaster_status` values to `GITHUB_OUTPUT` when that variable exists.
   * Keep the existing masked notice. Never emit endpoint, key, payload, breaking
     news, or arbitrary response fields.
   * Do not change dry-run or payload semantics.

4. `.github/workflows/podcaster-handoff-smoke.yml`

   * No production change is recommended. Preserve its environment, exact evidence
     verification, dry-run flag, and summary step.

5. `docs/operator-guide.md`

   * Replace the automatic post-merge description in Step 5 with the protected
     manual flow.
   * Document the required exact `week` and `publish_run_id`, environment setup
     prerequisite, no-duplicate authorization, and non-secret evidence fields.

6. `docs/pipeline-validation.md`

   * Replace the artifact-handoff statement that says sync triggers Podcaster.
   * State that deploy performs exact dry-run smoke and real generation is a
     separate protected manual dispatch after merge.

7. `architecture.md` and `docs/devsecops/checkov-baseline.md`

   * Clarify environment-scoped real credentials and the required-run-ID dispatch
     input.
   * Keep the justified CKV_GHA_7 skip, but update its inline explanation to say
     the required run ID selects retained evidence and does not alter build output.

Do not mark `docs/review/data-observatory-relaunch/owner-action-register.md` or
`status-of-record.md` complete in the implementation PR. Update those records only
after the admin policy, approved real run, downstream conclusion, URL review, and
maintainer evidence exist.

### Exact test changes

1. Replace
   `tests/test_pipeline.py::test_podcaster_handoff_triggers_post_merge_from_sync_not_crawl`
   with assertions that neither crawl nor sync contains a real Podcaster step,
   `PODCASTER_ENDPOINT`, `PODCASTER_API_KEY`, or `scripts/podcaster_handoff.py`.

2. Add a trigger-workflow test in `tests/test_pipeline.py` that asserts:

   * The only trigger is `workflow_dispatch`.
   * `publish_run_id` is required.
   * Job environment is exactly `podcaster-real-generation` and differs from
     `podcaster-release-smoke`.
   * Checkout uses the default branch.
   * Manifest construction includes both week and run ID and has no `find`,
     `tail -1`, or “most recent” fallback.
   * Manifest metadata is checked against the requested week and run ID.
   * Real invocation includes `--require-merged` and excludes
     `--podcaster-dry-run` and `--force`.
   * The evidence step uses `if: always()` and the Actions run URL, exact manifest
     identity, article digest, job ID, and response status.

3. Add
   `tests/test_sync_publish_workflow.py::test_publish_sync_never_dispatches_podcaster`
   as a focused negative regression test. This overlaps intentionally with the
   pipeline test because the no-side-effect invariant belongs to the sync workflow.

4. Add tests in `tests/test_podcaster_handoff.py` that patch `GITHUB_OUTPUT`, run a
   successful mocked handoff, and assert only escaped `podcaster_job_id` and
   `podcaster_status` are written. Add a no-`GITHUB_OUTPUT` case to preserve local
   CLI behavior and a failure case proving no success outputs are written.

5. Keep the existing
   `test_podcaster_smoke_workflow_exercises_real_weekly_payload_shape` unchanged as
   the regression guard for dry-run smoke, exact article bytes, promotion evidence,
   source-manifest hydration, environment separation, and evidence retention.

### Validation commands

```bash
uv run --no-sync pytest -q \
  tests/test_pipeline.py \
  tests/test_podcaster_handoff.py \
  tests/test_sync_publish_workflow.py
```

```bash
uv run --no-sync ruff check scripts/podcaster_handoff.py \
  tests/test_pipeline.py tests/test_podcaster_handoff.py \
  tests/test_sync_publish_workflow.py
uv run --no-sync ruff format --check scripts/podcaster_handoff.py \
  tests/test_pipeline.py tests/test_podcaster_handoff.py \
  tests/test_sync_publish_workflow.py
```

```bash
zizmor .github/workflows/
checkov --directory . --framework github_actions dockerfile secrets \
  --skip-path node_modules --skip-path .venv --compact --soft-fail
```

Review the workflow diff and confirm that the only remaining automatic Podcaster
call is the smoke workflow with `--podcaster-dry-run`. Do not run either Podcaster
workflow as a validation probe.

### Safe rollout order

1. Admin creates `podcaster-real-generation`, limits it to `main`, configures the
  intended reviewer, enables prevent self-review, and disables bypass if policy
  allows.
2. Admin stores the real endpoint variable and API key as environment-scoped values.
3. URL and Hermes review the proposed workflow and secret scope; the Podcaster
  maintainer confirms idempotency or authorizes one exact week/run ID.
4. Merge the repository change after local and CI validation. Do not dispatch it
  during implementation validation.
5. An authorized operator manually dispatches one exact week/run ID from `main`.
6. The environment approver reviews and approves the waiting job.
7. Retain the Actions URL and deployment review, then have the Podcaster maintainer
  resolve the returned job ID to a final downstream conclusion.

## Evidence

### Repository evidence

* `.github/workflows/trigger-podcast.yml`
* `.github/workflows/sync-publish-to-main.yml`
* `.github/workflows/podcaster-handoff-smoke.yml`
* `.github/workflows/deploy-site.yml`
* `scripts/podcaster_handoff.py`
* `tests/test_pipeline.py`
* `tests/test_podcaster_handoff.py`
* `tests/test_sync_publish_workflow.py`
* `docs/operator-guide.md`
* `docs/pipeline-validation.md`
* `docs/devsecops/checkov-baseline.md`
* `docs/review/data-observatory-relaunch/owner-action-register.md`
* `docs/review/data-observatory-relaunch/security-review.md`
* `.copilot-tracking/research/subagents/2026-08-02/claracle-acceptance-gates-followup-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-protected-acceptance-gates-research.md`

### External evidence

* [GitHub: Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
* [GitHub: Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

The GitHub documentation confirms that required reviewers, prevent self-review,
deployment branches/tags, administrator bypass, environment secrets, and environment
variables are environment settings. It also confirms that a missing environment is
created without protection rules or secrets when first referenced by a workflow.

## Recommended Next Research

* [ ] Confirm whether SquadScope-Podcaster deduplicates repeated week/run requests
  and where that contract is documented.
* [ ] Confirm the named environment reviewer and whether URL, Hermes, and the
  Podcaster maintainer require separate procedural sign-offs.
* [ ] Confirm whether the repository plan supports disabling administrator bypass.
* [ ] Confirm whether dry-run and real generation can use separate Podcaster API
  credentials; this determines whether the repository-level credential can be
  removed completely.
* [ ] Define the maintainer-owned lookup from returned Podcaster `job_id` to final
  downstream conclusion and retained evidence URL.

## Clarifying Questions

* Who is the required GitHub environment reviewer for real generation?
* Must URL, Hermes, and the Podcaster maintainer all approve, or is one environment
  approval plus separate recorded sign-offs sufficient?
* Does SquadScope-Podcaster guarantee idempotency for the exact week/run ID selected
  by this workflow?
* Can the smoke and real environments use distinct endpoint credentials?
