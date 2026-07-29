---
title: "State of Open Source AI 2026"
date: "2026-07-29T13:21:48+00:00"
draft: false
summary: "A public, downloadable snapshot of AI-adjacent GitHub projects observed by Claracle from 2026-W21 through 2026-W31."
description: "State of Open Source AI 2026: public GitHub project statistics, languages, licenses, recurring projects, and a MIT-licensed Claracle dataset download."
categories: ["state-of", "datasets"]
tags: ["open-source-ai", "github", "datasets", "ai-agents", "llm"]
---

Claracle's first public dataset covers **663 AI-adjacent GitHub repositories** observed across **1,545 weekly repo observations** from **2026-W21 through 2026-W31**. The export screened **4,602 public repo observations** from the local weekly crawl archive and kept records whose public name, description, or topics matched AI-adjacent terms such as AI, LLM, agent, MCP, RAG, machine learning, or model context protocol.

Download the MIT-licensed dataset:

- [CSV: top GitHub projects](/datasets/open-source-ai-github-projects-2026/top-github-projects.csv)
- [Dataset metadata](/datasets/open-source-ai-github-projects-2026/dataset-metadata.json)
- [MIT license](/datasets/open-source-ai-github-projects-2026/LICENSE.txt)
- [Citation and attribution note](/datasets/open-source-ai-github-projects-2026/CITATION.md)

## What is in the dataset

Each row is one public repository aggregate, not a raw crawl record. Fields include repository name, GitHub URL, primary language, latest observed license, first and last observed week, weeks observed, latest observed stars, first observed stars, observed star change, maximum observed forks, whether the repo appeared in the trending or new bucket, and its most common public topics.

The export deliberately excludes README text, private data, tokens, cache payloads, user account data, unpublished API calls, and non-public repositories.

## Headline numbers

| Metric | Value |
| --- | ---: |
| Source repo observations screened | 4,602 |
| AI-adjacent repo observations exported | 1,545 |
| Distinct exported repositories | 663 |
| Repositories observed in at least four weeks | 104 |
| Repositories seen in the trending bucket | 119 |
| Repositories seen in the new bucket | 546 |

## Languages: Python leads, TypeScript follows

Python is the largest implementation language in the exported set, followed by TypeScript and JavaScript.

| Language | Repositories |
| --- | ---: |
| Python | 218 |
| TypeScript | 141 |
| JavaScript | 65 |
| Rust | 30 |
| Shell | 21 |
| HTML | 20 |
| C# | 15 |
| Go | 14 |

The shape matches the editorial pattern we have seen all year: infrastructure, agent orchestration, and model-adjacent tools remain Python-heavy, while application shells, workflow products, and coding-agent interfaces skew toward TypeScript and JavaScript.

## Licenses: MIT dominates the observed AI slice

The dataset itself is published under MIT. Among the public projects observed inside the dataset, MIT is also the most common repository license.

| Project license | Repositories |
| --- | ---: |
| MIT | 358 |
| Apache-2.0 | 79 |
| NOASSERTION | 65 |
| AGPL-3.0 | 28 |
| GPL-3.0 | 16 |

`NOASSERTION` means the source crawl did not carry a resolved SPDX-style license for that project in the observed record; it is not a claim that the project is unlicensed.

## Persistent projects and fast movers

The top public AI-adjacent repositories by latest observed stars include [openclaw/openclaw](https://github.com/openclaw/openclaw), [obra/superpowers](https://github.com/obra/superpowers), [affaan-m/ECC](https://github.com/affaan-m/ECC), [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), [n8n-io/n8n](https://github.com/n8n-io/n8n), [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow), [anomalyco/opencode](https://github.com/anomalyco/opencode), [mattpocock/skills](https://github.com/mattpocock/skills), [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT), and [ollama/ollama](https://github.com/ollama/ollama).

Several projects show large observed star changes inside this May-to-July window, including agent-skill and coding-agent collections. Treat those changes as observed differences between weekly crawl records, not as complete lifetime growth curves.

## Topics: agents are the center of gravity

The most common public topics point to agent tooling rather than generic model demos.

| Topic | Mentions |
| --- | ---: |
| ai | 448 |
| ai-agents | 225 |
| claude-code | 149 |
| chatgpt | 112 |
| agent | 109 |
| anthropic | 99 |
| claude | 97 |
| llm | 89 |
| deep-learning | 82 |
| machine-learning | 82 |
| agents | 80 |
| deepseek | 77 |

The practical reading: open-source AI in this slice is less about one model family and more about packaging model access into tools, agents, command-line workflows, local systems, and automation layers.

## Methodology and source citation

This page is generated from the downloadable dataset and its metadata. The dataset is a read-only export from checked-in Claracle artifacts:

- `data/raw/2026-W21.json`
- `data/raw/2026-W22.json`
- `data/archive/recovered-W23-W29/2026-W23/2026-W23.json`
- `data/archive/recovered-W23-W29/2026-W24/2026-W24.json`
- `data/archive/recovered-W23-W29/2026-W25/2026-W25.json`
- `data/archive/recovered-W23-W29/2026-W26/2026-W26.json`
- `data/archive/recovered-W23-W29/2026-W27/2026-W27.json`
- `data/archive/recovered-W23-W29/2026-W28/2026-W28.json`
- `data/raw/2026-W29.json`
- `data/raw/2026-W30.json`
- `data/raw/2026-W31.json`

The original public source for repository names, URLs, stars, forks, languages, licenses, and topics is GitHub repository search and public repository pages/API responses. See the [methodology](/methodology/) page for Claracle's crawl cadence, ranking caveats, and source-bias limits.

## Exposure review

Hermes exposure check: **pass**. The published files contain only public GitHub repository metadata and derived aggregates. No secrets, private repository content, API tokens, account data, cache internals, unpublished API responses, or personal data are exposed.
