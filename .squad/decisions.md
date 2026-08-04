### 2026-08-04T12:58:39Z: Security decision — `podcaster-real-generation` self-review amendment

**By:** Hermes (Security & Threat Analyst), requested by jmservera

**What:** Accepted-with-conditions the disabling of `prevent_self_review` on the
`podcaster-real-generation` GitHub Actions environment. The flag had deadlocked approval
of the only real Podcaster-generation dispatch because jmservera (solo maintainer) was
also the only configured environment reviewer, and GitHub does not let a user approve
their own deployment when `prevent_self_review: true`.

**Why:** Self-review protection normally guards against an author quietly approving their
own deployment without independent scrutiny. That boundary does not meaningfully exist in
this repo today regardless of this flag, because the same account (jmservera) already has
admin/write access to `main`, the workflow file, and the environment's secrets and
protection rules — an account compromise that could self-approve could equally edit the
workflow or protection rules directly. The controls that actually bound residual risk are
independent of reviewer identity: `branch_policy` restricting deployment to `main`, the
job's `if: github.ref == 'refs/heads/main'` guard, required exact `week`/`publish_run_id`
inputs, fail-closed manifest `content_sha256`-vs-merged-article validation
(`--require-merged`), no secret values ever logged, and the retained per-run evidence step
summary.

**Compensating controls required (solo-maintainer usable, not "add a second reviewer"):**

* Environment `wait_timer` on `podcaster-real-generation` to force a cooling-off period
  before a self-approved deployment can proceed. Applied 2026-08-04: set to 10 minutes.
* Cross-check dispatch inputs (`week`, `publish_run_id`) against a pre-dispatch note of
  intent before approving — approval currently gates the job before the manifest is
  fetched/validated, so there is nothing else to check pre-approval.
* Mandatory post-run check of the retained evidence step summary (manifest/article
  SHA-256, downstream Podcaster job status) after every run — retention alone is not
  review.
* Revert `prevent_self_review` to `true` immediately if a second collaborator with
  environment-reviewer permissions ever joins the project.
* Revisit this environment's protection rules at the next security-review cycle.

**Disposition recorded:** [SEC-09](../../../../docs/review/data-observatory-relaunch/security-review.md#findings-and-dispositions),
severity Medium, owner Hermes.

**Scope note:** This decision covers only the security disposition of the self-review
amendment. URL's separate review of the environment's secret scope and workflow/pipeline
hardening (the other half of owner-action-register.md action 4, "Protected real Podcaster
run") is still open and was not addressed by this review.

**Files edited:**
* docs/review/data-observatory-relaunch/security-review.md
* docs/review/data-observatory-relaunch/owner-action-register.md
