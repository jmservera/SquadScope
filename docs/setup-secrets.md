# Setup secrets

## Required secrets

### `GA_MEASUREMENT_ID`

SquadScope uses `GA_MEASUREMENT_ID` to enable Google Analytics 4 on the deployed Hugo site.

Set it on the upstream repository with:

```bash
gh secret set GA_MEASUREMENT_ID --body "G-XXXXXXXX"
```

## Fork-safety behavior

`hugo.toml` defaults `params.ga_measurement_id` to an empty string. The deploy workflow maps the repository secret to `HUGO_PARAMS_GA_MEASUREMENT_ID`; Hugo exposes that environment override as `params.ga.measurement.id`, and the analytics partial uses it only when the secret exists.

Forks do not inherit repository secrets, so fork builds render with no analytics by default. This is intentional: forks must not silently send traffic to the maintainer's GA property.

## Opting out

Maintainers can disable analytics entirely by unsetting the repository secret:

```bash
gh secret delete GA_MEASUREMENT_ID
```
