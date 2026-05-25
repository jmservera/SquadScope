+++
title = 'Methodology'
date = '2026-05-25T00:00:00+02:00'
draft = false
summary = 'How SquadScope finds, ranks, and explains GitHub trend signals.'
description = 'Plain-English methodology for SquadScope source selection, scoring, ranking, and known bias limits.'
+++

## What this page is for

SquadScope is a weekly, AI-assisted read on developer and open-source momentum. We use automated crawls to find candidate projects, then generate editorial briefs from that evidence. This page explains where we look, how we rank what we find, and how readers should account for the gaps.

## Where we look

We start with GitHub repository search in `scripts/crawl.py`. On the general weekly crawl, we look for repositories created during the current seven-day window and repositories pushed during that same window, with both searches requiring more than 50 stars. Results are sorted by stars through the GitHub search API, deduplicated, checked for a README, and filtered to remove forks, templates, missing descriptions, homework/course material, demos, and other low-signal patterns. Topic-specific crawls can replace the default search with configured primary and secondary topic queries.

We also ingest press context. Today the automated press source is **TechCrunch RSS**, crawled by `scripts/techcrunch_crawler.py` over the same default seven-day window. That crawler extracts titles, summaries, categories, GitHub links, and likely company or project names, then keeps technology/open-source relevant articles for correlation. We do not currently ingest The Verge, Wired, Ars Technica, Hacker News, Reddit, non-English outlets, or paywalled newsletters as first-class automated sources. If we add those sources, this page should change.

The cadence is weekly. Unless an operator passes explicit dates, the GitHub and TechCrunch crawls look back seven days from the crawl time and write an ISO-week artifact such as `2026-W22.json`.

## How we score and rank

Raw GitHub results are not treated as a final ranking by themselves. `scripts/crawl.py` first records two buckets: new repositories and trending repositories. New repos are sorted by star count. Trending repos use prior weekly star snapshots when available, so a project with a strong week-over-week increase can rise above a project that is simply large. The weekly `signals` object summarizes common repo topics across the collected set; those topics help the analysis describe broad movement instead of only individual winners.

For topic channels, `scripts/score_repos.py` can compute a 0-100 relevance score. The score is capped and additive: up to 25 points for total stars, up to 25 for stars gained, up to 15 for language fit, up to 25 for matching configured topics, and up to 10 for freshness. Stars and stars gained use logarithmic scales, so very large projects still get credit but do not grow without limit. Topic matching caps at three matching topics. Defaults include a 20-star minimum, 10 stars gained, a 365-day freshness window, and a minimum relevance score of 40 unless the topic config changes them.

`signals.json` is not a separate source; in the current payload, `signals` is the structured summary generated from crawled repositories. `scripts/momentum_tracker.py` adds a hindsight check for press-correlated repos: after two or four weeks, a repo is marked sustained if its later stars gained are at least 20% of the initial gain; otherwise it is marked faded. The recorded decay rate is `1 - current / initial`, clamped between 0 and 1.

## Biases readers should account for

- **English-language source bias:** GitHub metadata and the current TechCrunch feed favor English-language projects and coverage; treat non-English ecosystem absence as under-observation, not lack of activity.
- **High-star bias:** The default crawl requires more than 50 stars and sorts by stars, so important niche projects can be missed until they are already visible.
- **US and Bay Area press bias:** TechCrunch coverage reflects a US startup lens; read press correlation as one narrative input, not a global technology map.
- **BigCo signal-strength bias:** Large companies create more repos, launches, docs, and articles, so their activity can look more important than quieter independent work.
- **Survivorship bias:** We mostly see projects that remain public and crawlable; failed experiments, abandoned private work, and deleted repos are largely invisible.
- **Recency bias:** A weekly window is good at catching spikes but can miss slower ecosystem shifts; use monthly and yearly rollups for longer arcs.

## What we do not do

We do not sell paid placements, accept sponsor influence over selection, or reserve ranking slots for partners. Editorial articles are AI-generated from collected signals; see the site footer disclosure and [About](/about/) page for that operating model. We do not retroactively rewrite past articles after publication. Until the dedicated errata process from issue #209 lands, corrections and concerns should be raised through [GitHub issues](https://github.com/jmservera/SquadScope/issues/new).

## Future work

We want this methodology to become more measurable. The next improvements are adding non-English source coverage, expanding hindsight validation for past calls (see [issue #38](https://github.com/jmservera/SquadScope/issues/38)), and adding a source-diversity metric to the public cost dashboard so readers can see whose signals the pipeline tends to hear.
