---
title: Data Observatory Relaunch Security Review
description: Repository security and privacy review of Observatory generation, lifecycle, datasets, embeds, browser tools, analytics, and deployment secrets
author: SquadScope Squad
ms.date: 2026-08-02
ms.topic: reference
keywords:
  - security review
  - privacy
  - prompt injection
  - data observatory
estimated_reading_time: 10
---

## Review status

> Reconciliation (2026-08-07): the findings below capture the 2026-08-02 through
> 2026-08-04 review-pass state and are retained as the historical record. NFR-004
> was subsequently **approved on 2026-08-06** — all ten findings (SEC-01 through
> SEC-10) carry dated dispositions and jmservera recorded sponsor acceptance. The
> authoritative disposition surface is
> [security-sign-off-checklist.md](security-sign-off-checklist.md); see also the
> [status of record](status-of-record.md).

Repository review was reconciled with current controls on 2026-08-02. Hermes has now verified and
dispositioned SEC-01 through SEC-05 (2026-08-04): SEC-01 through SEC-04 are approved, and SEC-05 is
accepted with conditions rather than a plain accept. SEC-08's Hermes sign-off and jmservera's sponsor
acceptance remain outstanding and were not part of this pass.
NFR-004 is not accepted, and the relaunch security gate remains open until every open finding carries
a disposition and jmservera records sponsor acceptance.

This record does not claim production behavior, secret presence, external service configuration,
or sponsor approval.

## Scope and trust boundaries

The review covers the following data path:

1. Public GitHub metadata and external article text enter checked-in crawl artifacts.
2. Sanitizers and prompt boundaries constrain untrusted text before analysis.
3. Generated weekly content, taxonomy registries, candidate evidence, repository histories, and
   lifecycle state become repository-reviewed inputs.
4. Generators produce public Markdown, JSON, CSV, and Hugo pages.
5. Hugo publishes static HTML, same-origin datasets, browser scripts, and embeddable chart frames.
6. Optional analytics loads only through the consent and build-secret path.
7. GitHub Actions holds deployment and Podcaster credentials outside generated content.

The principal boundaries are external text to the analysis prompt, analysis output to generated
frontmatter, repository data to public datasets, generated JSON to browser DOM, Claracle pages to
GitHub links, third-party sites to Claracle embed frames, and Actions secrets to public build output.

## Surface review

### Sanitization and prompt injection

`scripts/sanitize_repo_content.py` detects known injection phrases, escapes untrusted boundary
markers, applies length limits, and recursively sanitizes repository payloads. Prompt assembly fences
untrusted content, adds closing constraints, and uses canary leak detection. The standard test suite
contains prompt lint and red-team coverage.

`scripts/generate_content.py` revalidates generated frontmatter length, injection phrases, and
boundary markers. Hugo keeps `markup.goldmark.renderer.unsafe = false`, so generated Markdown cannot
introduce arbitrary raw HTML through normal rendering.

Residual risk remains because phrase matching cannot identify every semantic injection. New external
fields must pass through the same sanitization and boundary path before prompt use.

**SEC-05 recommendation for human decision:** accept the semantic false-negative risk only as a
defense-in-depth residual risk while retaining input sanitization, untrusted-content fencing, closing
prompt constraints, canary leak detection, output and frontmatter validation, prompt lint, and the
red-team corpus. Phrase matching detects known lexical patterns; it cannot reliably identify novel
wording, translation, encoding, or semantic paraphrases with equivalent intent. The retained controls
reduce the chance that one miss reaches publication but do not prove semantic detection. Hermes has
now reviewed this recommendation and accepted it with conditions rather than as a plain accept — see
[SEC-05 phrase-based injection detection risk assessment](#sec-05-phrase-based-injection-detection-risk-assessment-hermes).

### Candidate-title abuse

Candidate discovery combines repository-controlled topics, weekly tags, and analyzed headings.
Canonical and ignored terms reduce noise, and dynamic creation is disabled. `manage_topic_hubs.py`
now bounds candidate titles through `sanitize_text()`, rejects line breaks, boundary markers, HTML,
Markdown syntax, control characters, and known injection phrases, and serializes frontmatter through
structured YAML. `tests/test_topic_hubs.py` verifies that unsafe titles fail before any mutation.

The implementation condition for this finding is complete, and Hermes has now verified the control —
see [SEC-01 candidate-title sanitization verification](#sec-01-candidate-title-sanitization-verification-hermes).
Dynamic creation remains disabled until a human separately reviews the evidence and exact output for
the approved canary.

### Lifecycle evidence and deletion

Repository creation is disabled. When separately enabled, `observatory_repos.py` treats absence from
a crawl as insufficient deletion evidence. Reviewed lifecycle overrides and a persisted ledger carry
status. Confirmed deletions receive `deletion_confirmed_at` and `retained_until`; removal occurs only
after the configured three-year retention period and only for generator-owned pages.

The remaining risk is operator error in a lifecycle override. Review must pair the override, source
evidence, ledger diff, aliases, generated page, and any expiry removal. Hermes has now reviewed the
deletion evidence policy and approved it — see
[SEC-04 lifecycle deletion verification](#sec-04-lifecycle-deletion-verification-hermes).

`tests/test_observatory_repos.py` now exercises rename aliases, archive evidence, confirmed deletion,
three-year retention, expiry removal, absence that fails closed, and stable-ID migration. These
fixtures prove implementation behavior, not that the production corpus contains stable IDs or a
reviewed lifecycle transition.

### Public dataset exposure

Observatory JSON and CSV outputs are intentionally public. They contain public repository metadata,
weekly observations, topics, derived metrics, and provenance. They must not contain Actions inputs,
private repository data, prompt transcripts, credentials, email addresses, analytics identifiers,
or local filesystem paths.

`scripts/export_observatory_dataset.py` now defines exact production allowlists for the CSV,
top-repository metadata objects, and the metadata document. It also restricts `source_files` to the
eleven expected checked-in paths under `data/raw/` and
`data/archive/recovered-W23-W29/`. Runtime validation rejects added or missing keys, keeps
`metadata.fields` synchronized with the CSV schema, and requires weekly count keys to equal the
exported week list.

| Classification | Allowed fields |
| -------------- | -------------- |
| Public source identity | `repository`, `url`, `primary_language`, `latest_license`, `top_topics` |
| Public observations | `latest_stars`, `first_observed_stars`, `max_forks_observed`, `seen_in_trending`, `seen_in_new` |
| Derived public metrics | `rank_by_latest_stars`, `first_seen_week`, `last_seen_week`, `weeks_observed`, `observed_star_change` |
| Release metadata | Dataset/version/timestamp/source/selection/license, bounded counts and rankings, exact CSV fields, allowlisted source paths, exposure statement |

Publication remains a data-classification boundary. Any new CSV, metadata, or nested-object field
requires an intentional allowlist change, an exact-schema test update, and Hermes privacy review.
Hermes has now completed that privacy review for the current allowlists — see
[SEC-03 public export allowlist verification](#sec-03-public-export-allowlist-verification-hermes).

### Embed privacy and attribution

Embeddable charts are static Claracle iframe endpoints with visible attribution. The official
snippet now sets `referrerpolicy="no-referrer"`, so a publisher using it unchanged does not send the
embedding page URL as the iframe request referrer. Publishers control their own markup and can remove
or replace this attribute; Claracle cannot enforce the policy after a snippet is copied.

Analytics inside the iframe is frame-local, default-off, and enabled only after the visitor explicitly
accepts Claracle analytics in the consent UI rendered inside that frame. Consent collected by the
embedding site is neither inferred nor transferred. Browser third-party-storage restrictions may
prevent the Claracle consent choice from persisting, which can cause the frame to ask again, but
storage failure never enables analytics. The adapter records `chart_embed_view` only after the
frame-local consent callback enables it.

Rendered-snippet assertions, consent-wiring tests, and the Observatory browser analytics test provide
repository-executable evidence for this model. Production network/storage behavior and publisher
modifications remain outside repository control. Hermes has now recorded a privacy disposition for
the repository-controllable portion of this model — see
[SEC-02 embed referrer policy and consent isolation verification](#sec-02-embed-referrer-policy-and-consent-isolation-verification-hermes).

### Browser tool URL and DOM handling

The Star Velocity Explorer fetches a rendered same-origin dataset, checks for a repository array,
and uses DOM creation plus `textContent` for repository-controlled labels. It does not assign source
data through `innerHTML`. Outbound repository URLs are parsed and accepted only for HTTPS links on
`github.com`; invalid values become `#`. The browser sends no authenticated GitHub request and stores
no user query.

The result list is limited to 25 rendered rows, but the full generated dataset is downloaded and
filtered in memory. Dataset size and malformed numeric values are availability concerns, not a
credential boundary. Amy and Fry own performance and malformed-payload regression coverage.

### Analytics and privacy

The analytics identifier defaults empty and enters the production build through
`GA_MEASUREMENT_ID`. Cookie Consent controls analytics state, and Observatory events return without
sending when consent is absent or `gtag` is unavailable. Tool events contain bounded action names,
tool ID, and page path. Chart events may include a referrer host.

Repository inspection does not prove first-visit network behavior, cookie behavior, GA4 receipt, or
production secret configuration. Those checks remain external acceptance evidence.

### Secret handling and cross-repository calls

The deploy workflow maps `GA_MEASUREMENT_ID` and `GSC_SITE_VERIFICATION` from GitHub Actions secrets
to Hugo parameters. Forks do not inherit those secrets. Podcaster smoke and publish workflows use
`PODCASTER_API_KEY` from protected Actions contexts. Generated browser code contains no credential
for GitHub, GA4 administration, GSC, or Podcaster.

Secret values must never be copied into evidence, screenshots, command output, fixtures, or generated
datasets. Workflow logs and environment scoping require URL review. A successful repository test
does not prove protected-environment configuration or a downstream Podcaster run.

### Environment self-review amendment (solo maintainer)

The `podcaster-real-generation` environment's `prevent_self_review` protection rule was disabled on
2026-08-04 after it deadlocked the first real-generation dispatch: with jmservera as the only
configured reviewer, `prevent_self_review: true` made `current_user_can_approve` false for
jmservera's own run, with no second reviewer able to approve it instead.

**SEC-09 disposition:** Accept-with-conditions. Self-review protection exists to stop an author from
quietly approving their own deployment without independent scrutiny. In this repository the same
account (jmservera) already holds admin and write access to `main`, the workflow file, and the
environment's secrets and protection rules, so that independent-scrutiny boundary does not exist
today regardless of this one flag — an account compromise that could approve a self-dispatched run
could equally edit the workflow or protection rules directly. Disabling `prevent_self_review` removes
a deadlock, not an enforceable control. The controls that actually bound residual risk are unrelated
to reviewer identity: `branch_policy` restricting deployment to `main`, the job's own
`if: github.ref == 'refs/heads/main'` guard, required exact `week` and `publish_run_id` inputs,
fail-closed manifest `content_sha256`-versus-merged-article validation (`--require-merged`), no
secret values ever logged, and the retained per-run evidence step summary. None of these depend on
who clicks approve.

Because jmservera is currently the only maintainer, adding a second reviewer is not an available fix
and is not the recommended control. Instead, this disposition requires:

* An environment `wait_timer` so approval cannot happen in the same reflexive action as dispatch.
  Applied 2026-08-04: `wait_timer` set to 10 minutes on `podcaster-real-generation`.
* Before approving, cross-check the dispatch inputs (`week`, `publish_run_id`) against a pre-dispatch
  note of intent, since environment approval currently gates the job before the manifest is fetched
  or validated.
* After every run, actually open the retained evidence step summary and confirm the manifest and
  article SHA-256 values and downstream Podcaster job status, rather than treating retention alone as
  review.
* Revert `prevent_self_review` to `true` immediately if a second collaborator with
  environment-reviewer permissions ever joins the project — the deadlock this amendment fixes only
  exists for a single reviewer.
* Revisit this environment's protection rules at the next security-review cycle.

Adding a second human reviewer remains the strongest long-term fix if the team grows, but it is out
of scope for the solo-maintainer case this disposition covers.

### Protected Podcaster workflow pipeline hardening (URL review)

URL reviewed `.github/workflows/trigger-podcast.yml` and the `podcaster-real-generation`
environment for secret scope and pipeline hardening, separate from Hermes' SEC-09 self-review
disposition above.

**SEC-10 disposition:** the workflow's existing controls are sufficient. Top-level and job-level
`permissions` are `contents: read` only, with no `write` scope anywhere in the file.
`actions/checkout` and `actions/setup-python` are pinned by full commit SHA with a version
comment, matching the repository's pinning convention. `PODCASTER_ENDPOINT` and
`PODCASTER_API_KEY` are only reachable through the `podcaster-real-generation` environment, which
restricts `branch_policy` to `main`; the job's own `if: github.ref == 'refs/heads/main'` guard is
redundant defense-in-depth on top of that environment restriction, not a substitute for it, since a
`workflow_dispatch` run always executes the workflow YAML from the dispatched ref. The
`PODCASTER_API_KEY` secret is referenced only inside one step's `env:` block, is never echoed, and
is not written to `$GITHUB_STEP_SUMMARY`; the separate evidence step records only non-secret fields
(dispatcher, week, run ID, manifest/article paths and hashes, Podcaster status/job ID, run URL).
All three `workflow_dispatch` inputs (`week`, `publish_run_id`, `breaking_news`) reach `run:` steps
through `env:` indirection rather than direct `${{ }}` interpolation in the script body, which
avoids the classic Actions template-injection pattern. `concurrency` with
`cancel-in-progress: false` prevents overlapping real-generation dispatches for the same ref. The
`checkov:skip=CKV_GHA_7` comment on the `workflow_dispatch` block remains justified: `week`,
`publish_run_id`, and `breaking_news` select or annotate already-produced, retained evidence and do
not alter Hugo build output, consistent with the disposition already recorded for this workflow in
[the checkov baseline](../../devsecops/checkov-baseline.md). The
`git checkout origin/publish -- "$MANIFEST"` step cannot be used for path traversal or option
injection because `$MANIFEST` is built only from `$WEEK` and `$PUBLISH_RUN_ID`, both
regex-validated (`^[0-9]{4}-W[0-9]{2}$`, `^[0-9]+$`) before use, so neither can start with `-` or
contain `..`.

One gap: `week` and `publish_run_id` are pattern-validated before use, but the optional
`breaking_news` free-text input had no length bound or character validation before it is forwarded,
via `scripts/podcaster_handoff.py`, into the JSON payload sent to the external Podcaster endpoint.
The dispatch is already gated by required environment reviewer approval, so this was not an
injection vector inside this workflow, but it was inconsistent with the other two inputs and had no
bound on what gets sent to a third-party service. Fixed 2026-08-04: the "Derive paths from week
slug" step now rejects `breaking_news` over 500 characters or containing control characters,
alongside the existing `week` validation.

### SEC-06 repo-side secret and wiring check (URL)

URL performed a repo-side check of the SEC-06 secret and wiring claims (names and behavior only,
no values recorded): `GA_MEASUREMENT_ID` exists as a repository secret and the GA4 script renders
in the built site. `PODCASTER_API_KEY` exists at repo level and is correctly scoped to the
`podcaster-real-generation` environment. `PODCASTER_ENDPOINT` was read as a repo **variable**
(`vars.PODCASTER_ENDPOINT`) by every workflow that uses it, while a same-named repo **secret**
also existed and was never referenced by any workflow — confirmed orphaned and deleted 2026-08-04
(`gh secret delete PODCASTER_ENDPOINT`); the variable is unaffected and workflows continue to read
it normally. A `GSC_SITE_VERIFICATION` secret is absent, so this site's own GSC meta-tag
verification path is inactive; jmservera confirmed 2026-08-04 that GSC was already verified by a
different method and this secret is not needed.

This repo-side check does not close SEC-06: external verification (GA4 event receipt and the
Podcaster downstream confirmation) remains pending and out of repository-tooling scope. The GSC
processed-sitemap conclusion is unaffected by this secret and remains tracked separately in
owner-action-register.md's analytics and search acceptance section.

### SEC-01 candidate-title sanitization verification (Hermes)

Hermes verified `scripts/manage_topic_hubs.py`'s `safe_candidate_title()` and the shared
`sanitize_text()` path in `scripts/sanitize_repo_content.py`. Titles are bounded to 3-80 characters
and rejected outright, not merely truncated, when they contain a recognized injection phrase, a
boundary marker, an `http(s)://` prefix, `"---"`, `"developer message"`, or any character outside the
permissive title pattern, which excludes control characters, angle brackets, backticks, and Markdown
emphasis markers. `tests/test_topic_hubs.py::test_dynamic_topic_creation_rejects_unsafe_titles_without_mutation`
exercises quoted strings, colon-based overrides, `---`, embedded newlines, an embedded NUL byte,
Markdown bold, an HTML tag, a boundary-marker string, and direct injection phrases, and asserts the
entire workspace is byte-for-byte unchanged on rejection. Frontmatter is serialized through
`yaml.safe_dump(..., sort_keys=False, allow_unicode=True)` in `render_hub()`, not string
concatenation, and `test_dynamic_topic_creation_writes_structured_yaml` round-trips the result
through `yaml.safe_load`. `config/observatory.toml`'s `[topic_hubs.dynamic_creation]` block has
`enabled = false` today, so no dynamic candidate titles are created in production.

**SEC-01 disposition:** Approved. The sanitizer rejects rather than merely escapes adversarial
titles, structured YAML serialization is confirmed in code and tests, and dynamic creation is
confirmed disabled at the config level. No conditions.

### SEC-02 embed referrer policy and consent isolation verification (Hermes)

Hermes verified the official embed snippet in `layouts/partials/visuals/observatory-chart.html`,
which emits `referrerpolicy="no-referrer"` on every generated iframe snippet. `layouts/embeds/baseof.html`,
the template that actually renders inside that iframe, independently includes
`partials/cookie-consent.html` and loads `assets/js/observatory-analytics.js`, so the embedded
document runs its own separate Cookie Consent instance and its own `ObservatoryAnalytics.setConsent()`
call; a repository-wide search found no `postMessage`, `window.parent`, or `window.top` usage
anywhere in the analytics or consent code, so there is no bridge carrying the parent page's consent
state into the frame. `tests/visual/observatory-analytics.spec.mjs`'s
`'standalone frame uses only its own explicit analytics consent'` test embeds the chart at a genuinely
different origin inside a parent page that has already accepted analytics consent, and asserts the
frame sends zero analytics requests and no `chart_embed_view` event until the frame's own in-frame
consent UI is explicitly accepted, at which point exactly one bounded `chart_embed_view` event fires.
This is real cross-origin coverage, not same-origin path isolation.

**SEC-02 disposition:** Approved. The referrer policy and frame-local consent isolation are
implemented as described and covered by a genuine cross-origin browser test. The residual risk that a
publisher strips `referrerpolicy` from a copied snippet is already acknowledged in this doc and is
outside Claracle's control by design; no additional condition needed.

### SEC-03 public export allowlist verification (Hermes)

Hermes verified `scripts/export_observatory_dataset.py`. `PUBLIC_CSV_FIELDS`, `PUBLIC_METADATA_FIELDS`,
and `PUBLIC_TOP_REPOSITORY_FIELDS` are explicit tuples in code, not documentation-only lists, and
match this doc's classification table field-for-field. `validate_exact_keys()` compares the emitted
key set against the allowlist by set symmetric difference and raises on any deviation in either
direction, so an unlisted addition and an accidental omission both fail closed. `public_source_path()`
restricts `source_files` to a hardcoded set built from `PREFERRED_RAW_WEEKS` (5 weeks) and
`RECOVERED_WEEKS` (6 weeks), eleven paths total, and raises on anything outside `data/raw/` or
`data/archive/recovered-W23-W29/`. `tests/test_export_observatory_dataset.py::test_public_export_allowlists_are_exact_and_synchronized`
pins the exact allowlist tuples, and
`test_public_export_rejects_unlisted_fields_and_source_paths` adds an unlisted field to a real CSV
row and a real metadata sub-object and confirms both are rejected, alongside an out-of-tree source
path.

**SEC-03 disposition:** Approved. The allowlists are enforced in code with fail-closed validation on
both directions, and the test suite exercises the rejection path with concrete unlisted fields rather
than only asserting the happy path.

### SEC-04 lifecycle deletion verification (Hermes)

Hermes verified `scripts/observatory_repos.py` and `tests/test_observatory_repos.py`.
`config/observatory.toml`'s `[repo_pages]` block has `enabled = false` today, so no new repository
pages are generated in production, and `generate()` separately raises if lifecycle seed data is
supplied while `enabled` is true without an explicit config path, guarding against a silent
accidental enable. `deletion_retention()` requires `deletion_confirmed_at` on any `status = "deleted"`
override, rejects missing, invalid, or future confirmation dates, computes `retained_until` as
confirmation date plus the configured retention, and rejects an operator-supplied `retained_until`
that would shorten that window.
`test_deleted_override_fails_closed_without_valid_retention` confirms a deleted override without
valid retention fields raises before any content, derived, or taxonomy directory is written.
`test_absence_preserves_qualified_page_and_does_not_imply_deletion` confirms a repository dropping out
of the raw crawl data alone leaves its page and active status untouched.
`test_confirmed_deletion_is_retained_then_removed_only_after_expiry` confirms the page survives at the
retention boundary and is removed only the day after expiry.
`test_stable_id_rename_creates_alias_and_positive_archive_evidence` confirms a GitHub-ID-stable rename
produces a redirect alias and that an explicit `archived: true` field, not absence, is treated as
positive archive evidence.

**SEC-04 disposition:** Approved. Rename, archive, confirmed-deletion, retention, expiry removal, and
fail-closed-on-absence and fail-closed-on-invalid-override behavior are all implemented and covered by
dedicated tests, and repository-page creation is confirmed disabled today. The residual
operator-error risk this doc already calls out is a process risk, not a code gap; carrying it forward
as a review-discipline condition is reasonable rather than a blocker.

### SEC-05 phrase-based injection detection risk assessment (Hermes)

Hermes verified `scripts/sanitize_repo_content.py`, the prompt-assembly and output-validation code in
`scripts/analyze_fallback.py`, `scripts/canary_token.py`, and the red-team corpus in
`tests/test_prompt_injection_redteam.py`, `tests/test_redteam_corpus.py`, and
`tests/test_defense_chain_e2e.py`. The layered defenses described in this doc are real: phrase-based
reject-and-truncate sanitization, boundary-marker fencing with a closing security constraint enforced
by the CI prompt linter, a unique per-invocation canary token, and `validate_output_safety()` blocking
publication outright on a full canary leak and warning on a partial or boundary-marker leak. The
red-team corpus covers direct override, role manipulation, boundary escape, and social-engineering
categories.

Forming an independent view rather than accepting this doc's framing verbatim: `validate_output_safety()`
only detects canary-token leakage and boundary-marker reproduction in the model's output. It has no
mechanism to detect a semantic injection that successfully alters the analysis narrative, for example
a repository description that manipulates the model into writing biased or fabricated coverage,
without the output ever leaking the canary or the boundary markers. Phrase matching and the red-team
corpus both test known lexical attack patterns; neither is designed to catch a novel paraphrase
carrying equivalent intent. The described controls are strong against exfiltration and
prompt-structure leakage but weaker against silent narrative manipulation that never tries to leak
anything. The mitigating factor Hermes is relying on, which this doc does not cite for this finding:
per `docs/operator-guide.md`, generated analysis content is merged to the default branch through a
reviewed pull request rather than auto-published, so a human reviews the generated diff before it
reaches the public site. That review gate, not an automated control, is the actual backstop against a
semantic injection that evades every automated layer above.

**SEC-05 disposition:** Accept-with-conditions, not a plain accept. Hermes accepts the
phrase-matching, fencing, canary, and lint stack as adequate defense-in-depth for the
exfiltration and prompt-structure-leak risk it is actually built to catch, but does not accept it as
sufficient on its own for the semantic-manipulation risk, because no component here is designed to
catch that class of attack at all. This disposition is conditioned on: (1) the existing PR-review-before-merge
gate for generated content remaining in place; (2) the red-team corpus being revisited and expanded
whenever a real injection attempt, successful or caught, is observed in production, rather than
treated as a closed list; (3) any future change that lets generated content publish without human
review first requires a new Hermes review before it ships, since that would remove the one control
that currently bounds the semantic-injection gap. With those conditions, SEC-05 is closeable; without
an explicit human-review gate before publish, Hermes would reject rather than accept this residual
risk.

## Findings and dispositions

| ID     | Finding                                                                                    | Severity      | Owner                 | Disposition                                                                                                 |
| ------ | ------------------------------------------------------------------------------------------ | ------------- | --------------------- | ----------------------------------------------------------------------------------------------------------- |
| SEC-01 | Dynamic hub candidate titles require bounded sanitization and structured serialization      | High          | Farnsworth and Hermes | Approved 2026-08-04 — see [SEC-01 candidate-title sanitization verification](#sec-01-candidate-title-sanitization-verification-hermes) |
| SEC-02 | Embed snippets require an explicit referrer policy and cross-origin consent does not transfer | Medium        | Amy and Hermes        | Approved 2026-08-04 — see [SEC-02 embed referrer policy and consent isolation verification](#sec-02-embed-referrer-policy-and-consent-isolation-verification-hermes) |
| SEC-03 | Public export fields need a documented allowlist to prevent future accidental expansion    | Medium        | Bender and Hermes     | Approved 2026-08-04 — see [SEC-03 public export allowlist verification](#sec-03-public-export-allowlist-verification-hermes) |
| SEC-04 | Lifecycle deletion depends on manually reviewed overrides                                  | Medium        | Bender and Hermes     | Approved 2026-08-04 — see [SEC-04 lifecycle deletion verification](#sec-04-lifecycle-deletion-verification-hermes) |
| SEC-05 | Phrase-based injection detection has known semantic false-negative risk                    | Medium        | Hermes and Farnsworth | Accepted-with-conditions 2026-08-04 — see [SEC-05 phrase-based injection detection risk assessment](#sec-05-phrase-based-injection-detection-risk-assessment-hermes) |
| SEC-06 | GA4, GSC, and Podcaster secret behavior is not proven by repository inspection             | Medium        | URL and jmservera     | Repo-side wiring check by URL 2026-08-04 (no values recorded), orphaned `PODCASTER_ENDPOINT` secret deleted, `GSC_SITE_VERIFICATION` confirmed unneeded by jmservera; GA4/Podcaster external verification still pending — see [SEC-06 repo-side secret and wiring check](#sec-06-repo-side-secret-and-wiring-check-url) |
| SEC-07 | Browser tool uses safe DOM and a restricted outbound URL policy                            | Informational | Amy                   | Repository control verified; production and accessibility behavior pending                                  |
| SEC-08 | Raw HTML rendering remains disabled                                                        | Informational | Amy and Hermes        | Repository control verified; Hermes sign-off pending                                                        |
| SEC-09 | `prevent_self_review` disabled on `podcaster-real-generation` because the sole reviewer is also the sole dispatcher (solo-maintainer deadlock) | Medium | Hermes | Accept-with-conditions 2026-08-04: no independent-scrutiny boundary existed to lose (same account already admins `main`, the workflow, and secrets); `wait_timer` set to 10 minutes (applied), plus pre-approval input cross-check, mandatory post-run evidence check, and reinstating `prevent_self_review: true` if a second reviewer ever joins |
| SEC-10 | Optional `breaking_news` `workflow_dispatch` input had no length bound or character validation, unlike `week` and `publish_run_id` | Low | URL | Resolved 2026-08-04: permissions least-privilege, SHA-pinned actions, environment-scoped secrets, branch/ref guard, concurrency control, no secret logging, and `env:` indirection for all inputs were already sufficient; added a 500-character length cap and control-character rejection on `breaking_news` in the same validation step as `week` |

## Required evidence before acceptance

- Hermes records approval, rejection, or accepted-risk rationale for SEC-01 through SEC-06 — SEC-01
  through SEC-05 satisfied 2026-08-04; SEC-06's Hermes-relevant portion still depends on URL/jmservera's
  pending external GA4/GSC/Podcaster verification
- Hermes verifies the implemented candidate-title sanitizer and adversarial rejection before dynamic topic creation is enabled — satisfied by SEC-01; enabling dynamic creation itself still needs a separate human review of the approved canary's evidence and exact output
- Embed privacy behavior has a documented and tested disposition — satisfied by SEC-02
- Public dataset schema receives a field-level privacy review — satisfied by SEC-03
- Lifecycle fixtures demonstrate rename, archive, confirmed deletion, retention, and expiry — satisfied by SEC-04
- A private first visit proves no analytics request or cookie before consent
- A consented visit proves only the expected bounded analytics events
- Workflow review confirms secrets remain scoped and masked — satisfied by SEC-10
- Podcaster evidence records a downstream conclusion without exposing its API key

## Sign-off

| Reviewer  | Role                                 | Status  | Date    | Notes                                                     |
| --------- | ------------------------------------ | ------- | ------- | --------------------------------------------------------- |
| Hermes    | Security and threat analysis         | Done with conditions | 2026-08-04 | SEC-01 through SEC-04 approved after code/test verification; SEC-05 accepted with conditions (PR-review-before-merge gate must stay in place, red-team corpus must grow with real attempts, any move to auto-publish needs a new Hermes review). SEC-08's Hermes sign-off is still outstanding and was out of scope for this pass |
| URL       | DevSecOps workflow and secret review | Done    | 2026-08-04 | Protected workflow and secret-scope review complete; see SEC-10. SEC-06's external GA4/GSC/Podcaster verification is separate and remains pending |
| jmservera | Sponsor and production owner         | Pending | Pending | Required for production rollout acceptance                |

NFR-004 status: **Pending security acceptance**. SEC-01 through SEC-05 now carry Hermes dispositions
(four approved, one accepted-with-conditions), but SEC-08's Hermes sign-off and jmservera's sponsor
acceptance remain outstanding, and repository implementation alone still does not substitute for the
external evidence items listed above.
