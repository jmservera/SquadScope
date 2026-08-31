---
title: "Supply-Chain Scanners, Skills Economies, and GitHub's Star-Farm Flood"
date: 2026-05-25T11:56:08Z
week: "2026-W22"
year: 2026
tags: [supply-chain-security, agent-skills, ai-memory, coding-agents, developer-tooling, noise-amplification, open-source]
categories: [weekly]
repos_featured: 420
stars_tracked: 16500000
top_repo: "perplexityai/bumblebee"
quality_score: 74
summary: "Week 22 delivers the clearest defensive-security signal of the year alongside a crystallising agent-skills economy — both nearly buried under the most concentrated coordinated star-farming campaign the crawl has caught."
---

## This Week's Trends

**Supply-chain security lands its most credible new tool of 2026.** [perplexityai/bumblebee](https://github.com/perplexityai/bumblebee) is a read-only Go scanner built by Perplexity AI to interrogate on-disk packages, browser extensions, and developer-tool metadata against known supply-chain compromise indicators. At 2,328 stars in five days with 181 forks, it is the week's highest-conviction new-repo signal: specific problem, defensible scope, credible team, real fork activity. Apple's open-sourcing of [apple/corecrypto](https://github.com/apple/corecrypto) adds a second data point — two significant platform and tooling actors moving toward transparency in the same week is not coincidence.

**Agent skills solidify as an ecosystem layer.** Last week's hint becomes this week's pattern. [open-gsd/get-shit-done-redux](https://github.com/open-gsd/get-shit-done-redux) (678 ⭐) and companion [open-gsd/gsd-pi](https://github.com/open-gsd/gsd-pi) (158 ⭐) deliver meta-prompting and spec-driven scaffolding; [aref-vc/tufte-claude-skill](https://github.com/aref-vc/tufte-claude-skill) (161 ⭐) packages Edward Tufte's visualization principles as a callable Claude Code skill; [kingbootoshi/directional-prompting](https://github.com/kingbootoshi/directional-prompting) (96 ⭐) formalizes outcome-first prompting methodology. In the trending set, [obra/superpowers](https://github.com/obra/superpowers) (205k ⭐) and [anthropics/skills](https://github.com/anthropics/skills) (140k ⭐) confirm this is now a category, not an experiment.

**Agent memory and observability mature into required primitives.** [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) (169 ⭐, Rust) solves cross-vendor long-term memory and agent handoff; [NanoFlow-io/engram](https://github.com/NanoFlow-io/engram) (119 ⭐, TypeScript) delivers hybrid SQLite+FTS5/LanceDB memory for OpenClaw agents; [jianshuo/ccglass](https://github.com/jianshuo/ccglass) (269 ⭐) takes the observability angle — a local proxy plus web dashboard to inspect exactly what an agent sends to the model. Trending [MemPalace/mempalace](https://github.com/MemPalace/mempalace) (52k ⭐) adds benchmarking context the memory space has lacked. Three independent teams hitting adjacent gaps in the same week is a pattern, not a coincidence.

**BYOK shims and open agent-service standards emerge.** [0xSero/codex-shim](https://github.com/0xSero/codex-shim) (504 ⭐) is the week's most pragmatic delivery: a local Responses-API shim letting Codex Desktop route to Factory BYOK models or GPT-5.5 passthrough. At the standard-setting end, [workos/auth.md](https://github.com/workos/auth.md) (94 ⭐) proposes an open protocol for agent service registration discoverable via a Markdown file at a domain root. Both answer the same market pressure: developers want model substitutability and open discovery, not locked-in platform stacks.

**Coordinated star farming peaks.** A tight cluster of repos — Nintendo Switch emulator kits, FL Studio unlock tools, Forza Horizon mod packs, Minecraft hack clients, Delta Executor Roblox hubs, HWID spoofers — arrived at 421–429 stars apiece, zero forks, all created within minutes on 2026-05-22. Claude-branded repos (Claude-Design-Studio, Mythos-Claude-Skill-Forge, claude-zeroclaw-agentics) ran the same playbook. Dozens of polymarket trading bots used keyword-repetition descriptions as a separate star-inflation vector. This is editorial noise, but it is also an ecosystem health signal: GitHub's discovery layer is under active, organized manipulation.

## Where Industry Meets Code

TechCrunch's six articles for the week covered SolarSquare's $60M round, spyware defense guidance for phone users, a nuclear startup SPAC, a Berlin search-marketing startup, Blue Origin's New Glenn clearance, and — most relevant — a reported piece on how founders and VCs use inflated ARR metrics to manufacture AI startup credibility. That last article is the clearest press-developer convergence of the week: TechCrunch is naming metric inflation in AI venture narratives at exactly the moment GitHub's new_repos feed is experiencing its own form of metric inflation through coordinated star farming. Neither story is aware of the other, but they describe the same underlying dynamic — manufactured signals crowding out honest ones.

The press ignored several of the week's most significant developer movements. The emergence of [perplexityai/bumblebee](https://github.com/perplexityai/bumblebee) as a supply-chain scanner got no coverage, even though software supply-chain risk has been a recurring TechCrunch topic since the 2020 SolarWinds episode. The agent skills economy — [open-gsd/get-shit-done-redux](https://github.com/open-gsd/get-shit-done-redux), [aref-vc/tufte-claude-skill](https://github.com/aref-vc/tufte-claude-skill), [workos/auth.md](https://github.com/workos/auth.md) — received no press attention despite representing a structural shift in how agent behavior is distributed and extended. The TechCrunch spyware-defense article aligns categorically with the week's security theme, but the press angle (consumer phone settings) and the developer angle (developer-workstation supply-chain scanning) point in entirely different directions and at entirely different audiences.

## Signal & Noise

The durable signal this week is concentrated and coherent across four categories: defensive security tooling ([perplexityai/bumblebee](https://github.com/perplexityai/bumblebee), [apple/corecrypto](https://github.com/apple/corecrypto)), agent skills as distribution mechanism ([open-gsd/get-shit-done-redux](https://github.com/open-gsd/get-shit-done-redux), [aref-vc/tufte-claude-skill](https://github.com/aref-vc/tufte-claude-skill), [kingbootoshi/directional-prompting](https://github.com/kingbootoshi/directional-prompting)), memory and observability as infrastructure ([akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory), [NanoFlow-io/engram](https://github.com/NanoFlow-io/engram), [jianshuo/ccglass](https://github.com/jianshuo/ccglass)), and model routing/standards ([0xSero/codex-shim](https://github.com/0xSero/codex-shim), [workos/auth.md](https://github.com/workos/auth.md)). Each cluster has the hallmarks of real ecosystem movement: multiple independent teams, specific problem statements, non-zero fork activity. MoonshotAI's entry with [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code) (343 ⭐) also registers as a geopolitical signal — a Chinese AI lab making a direct public bid for the coding-agent space is worth tracking regardless of the repo's current depth.

The noise this week is not background hum — it is an active manipulation campaign. The 421–429 star cluster is unambiguous coordination: identical star counts, zero forks, creation timestamps within minutes of each other, heterogeneous content (emulators, unlockers, hack clients) mixed with Claude-branded repos using the same technique. Polymarket trading bots with copy-paste, keyword-stuffed descriptions represent a separate spam vector. Stars_gained data remained absent for trending repos, so the trending list continues to function as a popularity catalog rather than a momentum leaderboard — the caveat from W21 persists. The temptation to read the `claude-code: 19` topic count in signals as agent-ecosystem momentum should be resisted: a significant share of that count comes from the spam cluster using Claude branding, not from genuine tooling.

## Blind Spots

The most consequential gap is agent execution security. [nkzw-tech/cloudsail](https://github.com/nkzw-tech/cloudsail) (90 ⭐) is the week's sole attempt at self-hosted agent sandboxing on Cloudflare, but it is isolated and under-resourced relative to the problem. As coding agents are routinely granted shell access, filesystem permissions, and API credentials, the blast radius of an agent error or compromise is expanding rapidly. There is no emergent category of runtime permission scoping, agent isolation, or behavioral boundary enforcement in this week's data — and no press narrative drawing attention to the gap. [scheidydude/codeindex](https://github.com/scheidydude/codeindex) (158 ⭐) hints at blast-radius analysis for AI-assisted development but is an analysis tool, not a runtime control.

The second gap is agent behavior testing. There is no shortage of tools to help agents write code, route to models, or persist memory. There is almost nothing in this week's crawl for verifying that agent actions are correct, bounded, and reproducible under varying inputs. Until agent behavior testing becomes a first-class category, production reliability claims for agent-built systems will remain assertions rather than verifiable properties.

## The Week Ahead

The skills and memory infrastructure trends are in active acceleration and unlikely to peak next week. Watch for domain-specific skill packages proliferating on the model of [aref-vc/tufte-claude-skill](https://github.com/aref-vc/tufte-claude-skill), and for early integrations between the memory layer ([NanoFlow-io/engram](https://github.com/NanoFlow-io/engram), [MemPalace/mempalace](https://github.com/MemPalace/mempalace)) and the observability layer ([jianshuo/ccglass](https://github.com/jianshuo/ccglass)). The coordinated star-farming surge either subsides as GitHub responds or intensifies and forces a pipeline filtering upgrade — next week's data will be diagnostic. The BYOK routing and agent-protocol work initiated by [0xSero/codex-shim](https://github.com/0xSero/codex-shim) and [workos/auth.md](https://github.com/workos/auth.md) will attract fast-follower implementations if either gains traction in practitioner communities over the coming days.

## Key References

### Notable Projects

- [perplexityai/bumblebee](https://github.com/perplexityai/bumblebee) — Read-only Go scanner for supply-chain compromise exposure in developer-tool metadata; the week's strongest new defensive-security release from a credible author.
- [open-gsd/get-shit-done-redux](https://github.com/open-gsd/get-shit-done-redux) — Meta-prompting and spec-driven development methodology for long-running coding agents; the highest-starred new entry in the emerging skills-ecosystem layer.
- [0xSero/codex-shim](https://github.com/0xSero/codex-shim) — Local Responses-API shim making Codex Desktop model-agnostic via Factory BYOK; the most pragmatic model-routing release of the week.
- [jianshuo/ccglass](https://github.com/jianshuo/ccglass) — Local proxy and web dashboard for inspecting what coding agents send to models; fills a real observability gap in the agent development workflow.
- [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) — Rust-based long-term memory for agent coding CLIs with cross-vendor handoff; directly addresses the context-persistence problem.
- [NanoFlow-io/engram](https://github.com/NanoFlow-io/engram) — Hybrid SQLite+FTS5/LanceDB memory plugin for OpenClaw agents; production-grade memory architecture rather than a proof-of-concept.
- [workos/auth.md](https://github.com/workos/auth.md) — Open protocol for agent service registration via a discoverable Markdown file; early-stage but potentially significant standard for agent-service interaction.
- [nkzw-tech/cloudsail](https://github.com/nkzw-tech/cloudsail) — Self-hosted Cloudflare-based sandboxes for coding agents; the week's best attempt at the agent execution-boundary problem.
- [aref-vc/tufte-claude-skill](https://github.com/aref-vc/tufte-claude-skill) — Claude Code skill distilling Tufte's data-visualization principles into chart generation; the clearest model of what domain-specific agent skills can look like.
- [apple/corecrypto](https://github.com/apple/corecrypto) — Apple's open-sourced cryptographic library; a platform-vendor transparency signal that landed in the same week as the supply-chain scanning theme.

### Press & Industry

- [How VCs and founders use inflated 'ARR' to crown AI startups](https://techcrunch.com/2026/05/22/how-vcs-and-founders-use-inflated-arr-to-kingmake-ai-startups/) — TechCrunch reporting on manufactured AI metrics; relevant counterpart to the coordinated star-farming pattern observed in GitHub new_repos this week.
- [These special phone and app features can help protect you from spyware](https://techcrunch.com/2026/05/23/you-dont-have-to-click-anything-to-get-hacked-anymore-heres-how-to-fight-back/) — TechCrunch security coverage aimed at consumers; categorically adjacent to the developer-facing supply-chain scanning work of perplexityai/bumblebee but pointing at a different audience and problem space.
- [SolarSquare in talks to raise up to $60M as India's rooftop solar market draws major VC interest](https://techcrunch.com/2026/05/23/solarsquare-in-talks-to-raise-up-to-60m-as-indias-rooftop-solar-market-draws-major-vc-interest/) — Climate/Startups funding news; no material developer-activity correlation in this week's crawl.
