# Decision: GA4 fork-safe secret injection

**Date:** 2026-05-25T22:30:00+02:00  
**Author:** Bender (Crawler/CI)  
**Status:** Proposed

## Context

SquadScope needs GA4 analytics for the upstream site, but forks must not silently report traffic to the maintainer's GA property. Repository secrets are not inherited by forks, so analytics must depend on an explicitly provided secret and render nothing when absent.

## Decision

Use a secret-default-empty pattern: Hugo config defines `params.ga_measurement_id = ""`, while the Pages deploy workflow injects `${{ secrets.GA_MEASUREMENT_ID }}` through `HUGO_PARAMS_GA_MEASUREMENT_ID`. Hugo maps that environment key to `params.ga.measurement.id`, and the analytics partial renders GA4 only when either config path is non-empty. The rendered scripts are marked with `data-cc-category="analytics"` so Cookie Consent v3 can load them only after analytics consent.

## Rationale

The empty config default is safe for forks and local builds. The environment override keeps the maintainer measurement ID out of source control while still enabling analytics in the upstream deployment. Consent-category script tagging keeps analytics dormant until the consent integration activates the analytics category.

## Impact

- Upstream deploys can enable GA4 by setting `GA_MEASUREMENT_ID`.
- Forks build without analytics by default.
- Maintainers can opt out by deleting the secret.
- Cookie consent integration can activate the tagged scripts without changing the GA4 partial.
