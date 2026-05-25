# BaseURL-aware links in data files

Date: 2026-05-25
Owner: Hermes

## Decision

Links inside `data/*.json` files must use `__TOKEN__` placeholders substituted by partials with Hugo URL helpers; never hardcode `/path/` prefixes inside data files.

## Rationale

SquadScope is currently deployed on GitHub project Pages under `/SquadScope/`, so root-relative links such as `/privacy/` resolve outside the site and can 404. If the site later moves to an apex/custom domain, Hugo URL helpers will render the same logical route correctly without changing legal-copy JSON.

## Implementation note

For cookie-consent copy, `data/cookieconsent.json` uses `__PRIVACY_URL__`, and `layouts/partials/cookie-consent.html` replaces it with `"privacy/" | relURL` before initializing Cookie Consent.
