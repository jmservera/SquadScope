+++
title = 'Methodology'
date = '2026-05-25T00:00:00+02:00'
draft = false
summary = 'How Claracle finds, ranks, and explains GitHub trend signals.'
description = 'Plain-English methodology for Claracle source selection, scoring, ranking, and known bias limits.'
+++

## What this page is for

Claracle is a weekly, AI-assisted read on developer and open-source momentum. We use automated crawls to find candidate projects, then generate editorial briefs from that evidence. This page explains where we look, how we rank what we find, and how readers should account for the gaps.

## Where we look

We start with GitHub repository search in `scripts/crawl.py`. On the general weekly crawl, we look for repositories created during the current seven-day window and repositories pushed during that same window, with both searches requiring more than 50 stars. Results are sorted by stars through the GitHub search API, deduplicated, checked for a README, and filtered to remove forks, templates, missing descriptions, homework/course material, demos, and other low-signal patterns. Topic-specific crawls can replace the default search with configured primary and secondary topic queries.

We also ingest external news context. The automated external-news crawler (`scripts/techcrunch_crawler.py`) reads its feed list from `config/external_news_sources.json` and currently fetches five RSS sources over the same default seven-day window:

- **TechCrunch** (`techcrunch.com`) — startup and technology press.
- **NVIDIA blog** (`blogs.nvidia.com`) — NVIDIA's first-party product and research blog.
- **Hugging Face blog** (`huggingface.co`) — Hugging Face's first-party blog.
- **MIT Technology Review** (`www.technologyreview.com`) — technology journalism and analysis.
- **GitHub blog** (`github.blog`) — GitHub's first-party product and engineering blog.

For each feed the crawler extracts titles, summaries, categories, GitHub links, and likely company or project names, then keeps technology/open-source relevant articles for correlation. The combined run is written to the canonical artifact `data/raw/{week}-external-news.json` (for example `data/raw/2026-W24-external-news.json`), which records every article, which source it came from, the per-source relevant-article and GitHub-link counts, and the source config used for the run. We do not currently ingest general-interest outlets such as The Verge, Wired, or Ars Technica, nor community aggregators like Hacker News or Reddit, non-English outlets, or paywalled newsletters as first-class automated sources. If we add or drop feeds in `config/external_news_sources.json`, this page should change.

The cadence is weekly. Unless an operator passes explicit dates, the GitHub crawl and the external-news crawl look back seven days from the crawl time and write ISO-week artifacts such as `2026-W24.json` and `2026-W24-external-news.json`.

## How we score and rank

Raw GitHub results are not treated as a final ranking by themselves. `scripts/crawl.py` first records two buckets: new repositories and trending repositories. New repos are sorted by star count. Trending repos use prior weekly star snapshots when available, so a project with a strong week-over-week increase can rise above a project that is simply large. The weekly `signals` object summarizes common repo topics across the collected set; those topics help the analysis describe broad movement instead of only individual winners.

For topic channels, `scripts/score_repos.py` can compute a 0-100 relevance score. The score is capped and additive: up to 25 points for total stars, up to 25 for stars gained, up to 15 for language fit, up to 25 for matching configured topics, and up to 10 for freshness. Stars and stars gained use logarithmic scales, so very large projects still get credit but do not grow without limit. Topic matching caps at three matching topics. Defaults include a 20-star minimum, 10 stars gained, a 365-day freshness window, and a minimum relevance score of 40 unless the topic config changes them.

`signals.json` is not a separate source; in the current payload, `signals` is the structured summary generated from crawled repositories. `scripts/momentum_tracker.py` adds a hindsight check for press-correlated repos: after two or four weeks, a repo is marked sustained if its later stars gained are at least 20% of the initial gain; otherwise it is marked faded. The recorded decay rate is `1 - current / initial`, clamped between 0 and 1.

## Responsible-AI caveats and bias limits

- **Source bias:** GitHub repositories and the current external-news feeds are only a slice of developer activity. Private work, enterprise pilots, package registries, community forums, regional press, and smaller newsletters are under-observed, so Claracle should not be read as a neutral or complete map of technology.
- **English-language source bias:** GitHub metadata and all five external-news feeds (TechCrunch, NVIDIA, Hugging Face, MIT Technology Review, and GitHub) publish primarily in English and cover mostly US and big-tech topics; treat non-English ecosystem absence as under-observation, not lack of activity.
- **Platform bias:** GitHub-centric measurement over-represents open-source projects, public launch behavior, star-seeking promotion, and communities that already use GitHub. Work happening on GitLab, SourceHut, Bitbucket, self-hosted forges, package registries, Discord, Slack, or behind company firewalls may be invisible.
- **High-star bias:** The default crawl requires more than 50 stars and sorts by stars, so important niche projects can be missed until they are already visible.
- **Vendor and corporate-blog bias:** Three of the five external-news feeds — the NVIDIA, Hugging Face, and GitHub blogs — are first-party, promotional sources. They cover their own products, launches, and partners, so they over-represent those vendors and frame news favorably. MIT Technology Review and TechCrunch are independent press but still skew toward English-language, US, and big-tech stories. Read all press correlation as narrative input, not a global or neutral technology map.
- **BigCo signal-strength bias:** Large companies create more repos, launches, docs, and articles — and several of our feeds are run by large companies — so their activity can look more important than quieter independent work.
- **Survivorship bias:** We mostly see projects that remain public and crawlable; failed experiments, abandoned private work, and deleted repos are largely invisible.
- **Recency bias:** A weekly window is good at catching spikes but can miss slower ecosystem shifts; use monthly and yearly rollups for longer arcs.

These caveats are part of the analysis, not a disclaimer that makes the output neutral. The AI-assisted write-up can still over-weight vivid examples, repeat gaps in source coverage, or describe a project more confidently than the evidence supports. Reader reports are welcome when a claim, framing, source choice, or safety implication needs review.

## Corrections and reader reports

Weekly articles include a footer link to report a correction, source concern, or safety concern through GitHub Issues. The link prefills the article URL and week so reports can be triaged against the exact published page.

When a report arrives, maintainers should:

1. **Triage the report.** Confirm the affected article/week, classify it as factual correction, source-quality issue, safety concern, bias/framing concern, or duplicate/out of scope, and ask for additional evidence only if the report cannot be evaluated from public sources.
2. **Update carefully.** Preserve the article's original publication context where possible. Fix clear factual errors, broken links, unsafe framing, or materially misleading source descriptions in the content or template that caused them.
3. **Leave visible correction notes.** For material changes, add an `errata` entry to the weekly article front matter with the correction date and a concise note. Minor typo/link fixes may be corrected without an errata note, but source, safety, ranking, or claim changes should be visible to readers.
4. **Close the loop.** Reply on the GitHub issue with what changed, what was not changed, and why. If the concern reveals a process gap, update this methodology or the relevant pipeline documentation.

Correction reports are not used to provide private support, remove criticism without evidence, or retroactively make every old article match the latest methodology. They are a path for readers to challenge evidence, improve safety, and make material updates visible.

## What we do not do

We do not sell paid placements, accept sponsor influence over selection, or reserve ranking slots for partners. Editorial articles are AI-generated from collected signals; see the site footer disclosure and [About](/about/) page for that operating model. We do not silently retroactively rewrite past articles after publication. Corrections and concerns should be raised through [GitHub issues](https://github.com/jmservera/SquadScope/issues/new?labels=correction%2Creader-report).

## Future work

We want this methodology to become more measurable. The next improvements are adding non-English source coverage, expanding hindsight validation for past calls (see [issue #38](https://github.com/jmservera/SquadScope/issues/38)), and adding a source-diversity metric to the public cost dashboard so readers can see whose signals the pipeline tends to hear.
