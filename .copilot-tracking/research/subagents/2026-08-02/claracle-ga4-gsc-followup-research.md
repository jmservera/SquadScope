<!-- markdownlint-disable-file -->
# Claracle GA4 and Google Search Console Follow-up Research

## Status

Complete as of 2026-08-02

## Research Questions

* What FR-035 repository-side work can be completed without Google credentials?
* Which GA4 and Google Search Console actions require jmservera account access?
* Should `ga_measurement_id` be driven by Hugo configuration, environment variables, or both?
* What are the cheapest executable validations for the selected approach?

## Scope

* `hugo.toml`
* Consent-gating layouts and scripts
* Growth evidence and FR-035 planning records
* GitHub issue #599, when available
* Relevant tests and repository instructions

## Findings

### Executive conclusion

FR-035 is partially implemented, not wholly unimplemented. The repository already has the required
fork-safe GA4 parameter path, dynamic consent-gated loading, GSC verification metadata path, Hugo
sitemap generation, workflow secret injection, unit coverage for workflow mapping and GSC rendering,
and a blocking Playwright consent suite. No new production analytics implementation is required before
the account-side work.

The remaining acceptance work is external. A names-only GitHub secret query showed that
`GA_MEASUREMENT_ID` exists and was last updated on 2026-06-13, while `GSC_SITE_VERIFICATION` does not
exist. A credential-free production probe on 2026-08-02 found GA configuration in the rendered home
page, no GSC verification meta tag, and a successful XML sitemap response:

```text
ga_config_present=yes
gsc_meta_present=no
sitemap_status=200
sitemap_content_type=application/xml
```

These observations disprove the status-of-record rationale that an empty checked-in
`ga_measurement_id` means GA4 is not deployed. They do not prove that the deployed ID belongs to the
intended property, that GA4 receives events, or that the required baseline has been captured.

### Current repository implementation

| Surface | Current behavior | Evidence |
| --- | --- | --- |
| Checked-in GA4 configuration | Empty by design for fork safety | `hugo.toml:22-24` |
| Checked-in GSC configuration | Empty by design | `hugo.toml:25-26` |
| Production parameter injection | Actions secrets map to Hugo environment overrides | `.github/workflows/deploy-site.yml:36-40` |
| GA4 render path | Supports flat config and Hugo's nested environment mapping; renders only when configured | `layouts/partials/analytics.html:1-11` |
| Consent gate | GA is disabled first; `gtag.js` is appended only after analytics consent | `layouts/partials/cookie-consent.html:44-101` |
| Custom events | Event names and fields are allowlisted; dispatch returns before consent | `assets/js/observatory-analytics.js:4-78` |
| GSC render path | Supports the new secret-backed parameter plus the legacy theme fallback | `layouts/partials/head.html:20-29` |
| Workflow contract test | Verifies both Actions secret mappings and CI's GA test ID | `tests/test_pipeline.py:265-284` |
| GSC render tests | Verify absent-by-default, environment override, precedence, and legacy fallback | `tests/test_rendered_seo_metadata.py:447-539` |
| Consent browser tests | Verify denied, accepted, reload, withdrawal, cookie clearing, and bounded events | `tests/visual/observatory-analytics.spec.mjs:1-180` |

### Repository-side work possible without Google credentials

No product behavior must be added to connect the existing paths. The following repository work can be
completed without signing in to Google:

1. Correct stale evidence and status wording after the account observations are supplied. In
   particular, `docs/review/data-observatory-relaunch/status-of-record.md:70` and
   `docs/prds/claracle-data-observatory-relaunch.md:138` should not use the empty fork-safe default as
   evidence that production GA4 is disconnected.
2. Update `docs/growth/ga4-gsc-baseline-2026-07-29.md` with dated, redacted observations supplied by
   jmservera. Repository authors can prepare and review the evidence structure without platform access,
   but must not invent values or copy secret tokens.
3. Clarify the comment in `hugo.toml:23`. It currently suggests writing the production ID into the
   file, while the implemented security decision and `docs/setup-secrets.md` require secret-backed
   environment injection and an empty checked-in default.
4. Run the workflow mapping test, Hugo rendering tests, local consent browser test, sitemap HTTP probe,
   and names-only secret inventory. These checks need repository, network, or GitHub access, but no
   Google credentials.
5. Optionally add a small Hugo render test for the GA parameter itself. The current blocking Playwright
   path already exercises it end to end with `G-TEST-OBSERVATORY`, so this is a test-speed improvement,
   not an FR-035 blocker.

Setting `GSC_SITE_VERIFICATION` in GitHub is also repository-side, but the token must first be obtained
from a Search Console property. The person setting it needs GitHub secret-management rights; they do
not need Google access if jmservera supplies the token through an approved private channel.

### Issue 599 context

GitHub issue #599 was opened by jmservera on 2026-07-29 and closed as completed on 2026-08-01. Its
acceptance criteria require GA4 receipt, a verified GSC property, sitemap submission, and a dated
baseline. The only owner follow-up comment records five remaining human actions: create or select the
Claracle GA4 property and web stream, set the production measurement ID, verify `claracle.com` in GSC,
submit the sitemap, and capture baseline values. The issue contains no later comment proving those
actions. Closure therefore records completion of agent-side wiring, not FR-035 operational acceptance.

Issue URL: [#599](https://github.com/jmservera/SquadScope/issues/599)

## Selected Approach

Keep the existing config-plus-environment design:

* Keep `params.ga_measurement_id = ""` and `params.gsc_site_verification = ""` in `hugo.toml`
* Inject production values through `HUGO_PARAMS_GA_MEASUREMENT_ID` and
  `HUGO_PARAMS_GSC_SITE_VERIFICATION` from GitHub Actions secrets
* Continue resolving both flat checked-in keys and Hugo's nested environment-key representation in the
  templates
* Never hardcode the production GA measurement ID or GSC verification token in source

For GSC, use the already-implemented URL-prefix property and HTML meta-tag verification flow for
`https://claracle.com/`. This is the cheapest path because it needs no DNS change and the template,
workflow mapping, documentation, and tests already exist. A Domain property would broaden coverage but
requires DNS-provider access and does not use the repository's current verification path.

Recommended completion sequence:

1. jmservera confirms that the existing deployed GA ID belongs to the intended Claracle property and
   web stream. Do not rotate the GitHub secret unless it is wrong.
2. jmservera adds or selects the GSC URL-prefix property and privately obtains its HTML-tag token.
3. A repository administrator sets `GSC_SITE_VERIFICATION`, deploys the reviewed revision, and confirms
   only the presence of the production meta tag.
4. jmservera clicks Verify in GSC and submits `https://claracle.com/sitemap.xml`.
5. jmservera performs a consented production visit, confirms GA4 Realtime receipt, and captures GA4/GSC
   values for one explicitly dated baseline window.
6. Hermes or the designated privacy reviewer records denied and granted production browser behavior.
7. A repository-only follow-up updates the baseline, status of record, and PRD acceptance note with
   redacted evidence and marks FR-035 complete only when every acceptance item is evidenced.

## Credential and Ownership Boundary

### Requires jmservera or delegated Google account access

* Create, select, or inspect the GA4 account, property, and web data stream. Google requires the Editor
  role to create properties or streams.
* Confirm that the deployed measurement ID maps to the intended Claracle stream.
* Observe Realtime receipt and capture GA4 acquisition/session baseline values.
* Add or select the Search Console property and obtain its verification token.
* Complete GSC ownership verification. A verified owner has the highest Search Console permission.
* Submit the sitemap in the verified property and capture submission, processing, performance, and
  indexing evidence.

These actions are assigned to jmservera by `docs/data-observatory-runbook.md:32-45` and issue #599.
They can be delegated only by granting the appropriate GA4 role and GSC owner/user access.

### Requires GitHub access but not Google credentials

* List secret names and timestamps without viewing values
* Set or rotate `GA_MEASUREMENT_ID` after an authorized person supplies the ID
* Set `GSC_SITE_VERIFICATION` after an authorized person supplies the token
* Trigger or inspect the Pages deployment and retain the Actions URL

GitHub does not expose Actions secret values after creation. Secret-name presence proves protected
configuration exists, not that it is correct.

### Requires neither Google nor privileged GitHub access

* Inspect and test templates, consent code, workflow expressions, and generated output with test IDs
* Probe the public home page for configuration presence without printing the ID
* Probe the public sitemap response and content type
* Prepare documentation and evidence placeholders

### Blockers

* `GSC_SITE_VERIFICATION` is absent from the repository secret inventory
* Production has no GSC verification meta tag as of 2026-08-02
* No retained evidence proves GA4 Realtime receipt or the intended property/stream mapping
* No retained evidence proves GSC ownership verification or sitemap submission
* All GA4/GSC baseline values remain pending
* Local Hugo render tests could not execute in this session because the `hugo` binary is absent

## Validation Commands

### Cheapest repository contract

```bash
python3 -m pytest -q \
  tests/test_pipeline.py::WorkflowConfigTests::test_deploy_workflow_maps_analytics_and_gsc_secrets_to_hugo_params
```

Observed result: `1 passed` when run as part of the focused four-test selection.

### GSC rendering contract

```bash
python3 -m pytest -q tests/test_rendered_seo_metadata.py -k gsc_site_verification
```

Requires Hugo. The three selected GSC tests skipped locally because `hugo` is not installed. CI installs
Hugo 0.161.1 and runs this file in the blocking production-site job.

### Full static production build

```bash
HUGO_PARAMS_GA_MEASUREMENT_ID=G-TEST-OBSERVATORY \
HUGO_PARAMS_GSC_SITE_VERIFICATION=testtoken123 \
hugo --minify --quiet --destination /tmp/claracle-fr035
```

Inspect only the test values in `/tmp/claracle-fr035/index.html`. Also build once with both variables
unset and confirm neither analytics configuration nor the GSC meta tag is emitted.

### Consent behavior

Use the same pinned dependencies and local server setup as `.github/workflows/ci.yml:110-177`, then run:

```bash
BASE_URL=http://127.0.0.1:1313 \
npx --no-install playwright test \
  --config tests/visual/playwright.config.mjs \
  tests/visual/observatory-analytics.spec.mjs \
  --project desktop-light
```

This is narrower than the full axe, responsive, and Lighthouse suite. It intercepts Google endpoints,
so it does not need a real GA property or send test events to Google.

### Protected configuration metadata

```bash
gh secret list --repo jmservera/SquadScope --json name,updatedAt \
  | jq '[.[] | select(.name == "GA_MEASUREMENT_ID" or .name == "GSC_SITE_VERIFICATION")]'
```

This command must never be replaced with a command that prints secret values.

### Credential-free production smoke

```bash
html="$(curl --fail --silent --show-error --location https://claracle.com/)"
printf 'ga_config_present=%s\n' "$(if grep -q 'gaMeasurementId' <<<"$html"; then echo yes; else echo no; fi)"
printf 'gsc_meta_present=%s\n' "$(if grep -q 'name=google-site-verification' <<<"$html"; then echo yes; else echo no; fi)"
curl --fail --silent --show-error --location --output /dev/null \
  --write-out 'sitemap_status=%{http_code}\nsitemap_content_type=%{content_type}\n' \
  https://claracle.com/sitemap.xml
```

This probe deliberately reports presence only and does not print the measurement ID or verification
token.

## References and Evidence

### Repository references

* `.github/copilot-instructions.md`
* `.github/workflows/ci.yml`
* `.github/workflows/deploy-site.yml`
* `.squad/decisions-archive.md:1303-1327`
* `assets/js/observatory-analytics.js`
* `docs/data-observatory-runbook.md`
* `docs/growth/ga4-gsc-baseline-2026-07-29.md`
* `docs/prds/claracle-data-observatory-relaunch.md`
* `docs/review/data-observatory-relaunch/security-review.md`
* `docs/review/data-observatory-relaunch/status-of-record.md`
* `docs/setup-secrets.md`
* `hugo.toml`
* `layouts/partials/analytics.html`
* `layouts/partials/cookie-consent.html`
* `layouts/partials/head.html`
* `tests/test_pipeline.py`
* `tests/test_rendered_seo_metadata.py`
* `tests/visual/observatory-analytics.spec.mjs`

### External references

* [Google Analytics setup](https://support.google.com/analytics/answer/9304153): signed-in Google
  account; Editor role required to create a property or add a data stream
* [Search Console ownership verification](https://support.google.com/webmasters/answer/9008080):
  property addition, verification methods, owner permissions, and verification persistence
* [Search Console Sitemaps report](https://support.google.com/webmasters/answer/7451001): submission,
  processing status, and the distinction between submitted and automatically discovered sitemaps

## Follow-on Questions

* Does the existing `GA_MEASUREMENT_ID` map to a dedicated Claracle production web stream?
* Has GSC already collected pre-verification data for a property that only needs ownership completion?
* Which approved private evidence location should retain redacted GA4 Realtime and GSC screenshots or
  exports?

## Clarifying Questions

These questions require jmservera account observations and cannot be answered from repository or public
evidence:

* Is the intended GA4 property already receiving consented production events?
* Does a Claracle GSC property already exist under the jmservera account?
* Should the dated baseline window begin at first verified receipt, relaunch approval, or a fixed
  calendar boundary?