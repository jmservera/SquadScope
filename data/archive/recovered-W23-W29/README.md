# Recovered raw weekly evidence — W23–W29 (issue #569)

This directory holds **raw weekly crawl evidence recovered unchanged** from
still-unexpired GitHub Actions `raw-data` artifacts. It is isolated under
`data/archive/` and explicitly provenance-marked; it is **not** a recrawl and
does not regenerate or substitute any data.

## Contents

- `2026-W23/` … `2026-W29/` — the per-week raw payloads, byte-identical to the
  files inside their source artifacts.
- `recovered-raw.sha256` — SHA-256 checksums of every recovered file.
- `provenance.json` — full inventory: for each week, the source **artifact ID**,
  **source run ID**, artifact `head_sha`, created/expires timestamps, the
  **original pipeline path** (`data/raw/…`), file size, and SHA-256.

## Provenance summary

| Week | Artifact ID | Source run ID | Artifact created | Expires |
|------|-------------|---------------|------------------|---------|
| 2026-W23 | 7330965888 | 26753498571 | 2026-06-01 | 2026-08-30 |
| 2026-W24 | 7480423082 | 27137991437 | 2026-06-08 | 2026-09-06 |
| 2026-W25 | 7680608990 | 27650616699 | 2026-06-16 | 2026-09-14 |
| 2026-W26 | 7786268089 | 27937940184 | 2026-06-22 | 2026-09-20 |
| 2026-W27 | 7942942491 | 28349393843 | 2026-06-29 | 2026-09-27 |
| 2026-W28 | 8099693880 | 28767491281 | 2026-07-06 | 2026-10-04 |
| 2026-W29 | 8268630097 | 29222289174 | 2026-07-13 | 2026-10-11 |

All seven weeks W23–W29 were recoverable; there are no expired/missing gaps.
The W29 artifact (`8268630097`, expires **2026-10-11**) is preserved here
durably before its expiry.

## Verify

```bash
cd data/archive/recovered-W23-W29
sha256sum -c recovered-raw.sha256
```

Each recorded hash was also verified source-bound: a fresh download of every
source artifact was extracted and its target-week files hashed to match the
values recorded here.
