# Hugo and Pagefind Build-Cost Experiment

> Report-only evidence. No blocking threshold or rollout authorization is defined.

Samples per variant: 3 (minimum).
Nearest-rank p95 is the observed maximum with three or five samples.

## Hugo

| Variant | Median ms | p95 ms | Delta ms | Delta % | Marginal ms/page |
|---|---:|---:|---:|---:|---:|
| baseline | 804 | 947.000 | null | null | null |
| topic_hubs | 806 | 856.000 | 2 | 0.249 | 0.400 |
| data_pages | 808 | 838.000 | 2 | 0.248 | 0.667 |
| repository_pages | 3116 | 3156.000 | 2308 | 285.644 | 8.776 |

## Pagefind

| Variant | Median ms | p95 ms | Delta ms | Delta % | Marginal ms/page |
|---|---:|---:|---:|---:|---:|
| baseline | 153 | 155.000 | null | null | null |
| topic_hubs | 153 | 154.000 | 0 | 0.000 | 0.000 |
| data_pages | 168 | 171.000 | 15 | 9.804 | 5.000 |
| repository_pages | 803 | 979.000 | 635 | 377.976 | 2.414 |
