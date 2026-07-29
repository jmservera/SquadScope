# Setup secrets

## Required secrets

### `GA_MEASUREMENT_ID`

SquadScope uses `GA_MEASUREMENT_ID` to enable Google Analytics 4 on the deployed Hugo site.
This repository secret already exists for production; GA4 will activate on the next deploy while
remaining disabled until the visitor grants analytics consent.

Set it on the upstream repository with:

```bash
gh secret set GA_MEASUREMENT_ID --body "G-XXXXXXXX"
```

### `GSC_SITE_VERIFICATION`

SquadScope uses `GSC_SITE_VERIFICATION` to render Google's URL-prefix verification meta tag during
the Pages deploy. Copy only the token from Google Search Console, not the full `<meta>` tag.

Set it on the upstream repository with:

```bash
gh secret set GSC_SITE_VERIFICATION --body "PASTE_GOOGLE_VALUE_HERE"
```

After the next deploy, click **Verify** in Google Search Console and submit the sitemap:
`https://claracle.com/sitemap.xml`.

## Fork-safety behavior

`hugo.toml` defaults `params.ga_measurement_id` and `params.gsc_site_verification` to empty strings.
The deploy workflow maps repository secrets to Hugo parameter overrides. The analytics and GSC meta
partials use those values only when the secrets exist.

Forks do not inherit repository secrets, so fork builds render with no analytics or GSC verification
meta by default. This is intentional: forks must not silently send traffic to the maintainer's GA
property or claim Claracle Search Console ownership.

## Opting out

Maintainers can disable analytics entirely by unsetting the repository secret:

```bash
gh secret delete GA_MEASUREMENT_ID
```

Maintainers can disable URL-prefix GSC meta verification by unsetting the repository secret:

```bash
gh secret delete GSC_SITE_VERIFICATION
```
