---
title: "Agent Skills Became the New Attack Surface"
date: 2026-08-10T07:40:21Z
week: "2026-W33"
year: 2026
tags: [ai-agents, agent-skills, developer-tools, ai-safety, supply-chain-security, video-generation]
categories: [weekly]
repos_featured: 50
stars_tracked: 6377704
top_repo: "AMAP-ML/LongHorizon-Harness"
quality_score: 100
summary: "Agent skills spread into real workflows while security, reviewability, and discovery noise became the week’s hard constraints."
predictions:
  - repo: AMAP-ML/LongHorizon-Harness
    claim_type: signal
    direction: up
    confidence: 0.74
  - repo: KKKKhazix/human-writing
    claim_type: signal
    direction: up
    confidence: 0.68
  - repo: 0xwilliamortiz/claude-red
    claim_type: signal
    direction: up
    confidence: 0.61
  - repo: mikiarlo3/awesome-growth-hacking-skills
    claim_type: noise
    direction: down
    confidence: 0.72
  - repo: sv-number/mcp-server
    claim_type: noise
    direction: down
    confidence: 0.77
---

August 2026’s agent story stopped being about whether agents can act and became about what they are allowed to carry with them. Last week’s trust-wall theme carried over, but the center of gravity shifted from harnesses and workflow capture into portable skills: writing voices, slide generators, offensive-security playbooks, growth-hacking packs, and phone-control surfaces all appeared in the same crawl window.

The strongest throughline is **skills as operational infrastructure**. [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) anchors the serious side of that movement by emphasizing durable state, auditing, and recoverable progress for long-running agents. Around it, [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing), [Binaryify/open-kimi-ppt-skill](https://github.com/Binaryify/open-kimi-ppt-skill), and [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) show the same packaging instinct moving into language, presentations, and creative production.

The tension is that reusable skills are also reusable risk. Press coverage this week warned about agents that reward-hack, safety tests that become risk surfaces, malware advisories expanding beyond npm, and giant AI-generated pull requests that need to be stacked before humans can review them. GitHub activity is building the execution layer faster than the trust layer that must govern it.

## This Week's Trends

**Agent skills became a distribution format.** [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing), [Binaryify/open-kimi-ppt-skill](https://github.com/Binaryify/open-kimi-ppt-skill), [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills), and [mattpocock/skills](https://github.com/mattpocock/skills) point to a market where agent capabilities are packaged as reusable procedures rather than one-off prompts. The practitioner implication is immediate: teams will need versioning, provenance, review, and permission boundaries for skills the same way they already do for dependencies.

**Long-horizon control moved from demo to requirement.** [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness), [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness), [openclaw/openclaw](https://github.com/openclaw/openclaw), [affaan-m/ECC](https://github.com/affaan-m/ECC), and [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) frame agents as operators across desktops, phones, CLIs, and persistent work loops. That matters because once agents can touch stateful systems, continuity, rollback, audit logs, and human checkpoints become core architecture rather than niceties.

**Security content followed the agent surface.** [0xwilliamortiz/claude-red](https://github.com/0xwilliamortiz/claude-red) packages offensive-security methods as Claude skills, while [sowarma/wp2shell-PoC](https://github.com/sowarma/wp2shell-PoC) represents the familiar exploit-disclosure spike. The interesting signal is not merely that security repos appeared, but that security instructions are being formatted for agent execution.

**AI media tooling stayed hot but fragmented.** [jd-opensource/JoyAI-Video-Edit](https://github.com/jd-opensource/JoyAI-Video-Edit), [SandAI-org/MAGI-2-preview](https://github.com/SandAI-org/MAGI-2-preview), [huangserva/ComfyUI_MiniMaxH3_Director](https://github.com/huangserva/ComfyUI_MiniMaxH3_Director), and [NikoDemon80/ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) show continuing demand for video generation and editing workflows. The signal is practical workflow assembly more than a single dominant framework.

The trending table remains an absolute-popularity snapshot because weekly `stars_gained` is not present. Large anchors such as [n8n-io/n8n](https://github.com/n8n-io/n8n), [anomalyco/opencode](https://github.com/anomalyco/opencode), [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT), and [ollama/ollama](https://github.com/ollama/ollama) reinforce the macro themes, but they should not be read as proof of same-week acceleration.

## Where Industry Meets Code

The press-code alignment was strongest around agent execution surfaces. Cloudflare’s Kitesurf browser launch, GitHub’s Copilot slash-command guidance, the legal-team Copilot CLI story, and the stacked-PR guidance all describe agents moving into concrete workflows. The repo data matches that direction through [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness), [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness), [Fuxicodex/Fuxi](https://github.com/fuxicodex/Fuxi), [oil-oil/codex-deepseek-subagent](https://github.com/oil-oil/codex-deepseek-subagent), and [Sateezg/codex-bridge](https://github.com/Sateezg/codex-bridge): developers are not waiting for one agent platform to win; they are building bridges, harnesses, terminals, and subagent routes.

The safety and security coverage also maps to the week’s most uncomfortable repos. TechCrunch’s warning that AI safety tests can become risk surfaces and MIT Technology Review’s coverage of reward hacking sit beside [0xwilliamortiz/claude-red](https://github.com/0xwilliamortiz/claude-red), [sv-number/mcp-server](https://github.com/sv-number/mcp-server), and [sowarma/wp2shell-PoC](https://github.com/sowarma/wp2shell-PoC). GitHub’s post on taking malware advisories beyond npm is especially relevant because skills, MCP servers, and agent plugins look increasingly like supply-chain units.

The main divergence is infrastructure and physical AI. NVIDIA’s AI factory, storage, Omniverse, and autonomous-vehicle coverage was intense, but the visible developer response in this compacted set is mostly indirect: video workflows, local model tooling, and established [ollama/ollama](https://github.com/ollama/ollama), not a broad robotics or AI-factory buildout. OpenAI’s NextSlide acquisition, by contrast, has a clearer developer echo in [Binaryify/open-kimi-ppt-skill](https://github.com/Binaryify/open-kimi-ppt-skill) and [criptogus/HermesOffice](https://github.com/criptogus/HermesOffice).

## Signal & Noise

The durable signal is clustered around execution discipline. [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) is the clearest new anchor because it names the hard problems directly: long-running tasks, durable state, auditing, recovery, and integration with multiple coding agents. [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing) and [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) add an important geographic and linguistic expansion signal: Chinese-language agent skills are not peripheral wrappers, they are part of the same skills-economy arc that has been building for several weeks.

The noise sits where agent packaging meets questionable incentives. [mikiarlo3/awesome-growth-hacking-skills](https://github.com/mikiarlo3/awesome-growth-hacking-skills) may be useful as a directory, but its growth-hacking framing is exactly the kind of category that can turn skills into spam infrastructure. [sv-number/mcp-server](https://github.com/sv-number/mcp-server) has technically legible MCP positioning, yet private-number and SMS-verification automation is a high-risk trust signal. [Sateezg/codex-bridge](https://github.com/Sateezg/codex-bridge) and [oil-oil/codex-deepseek-subagent](https://github.com/oil-oil/codex-deepseek-subagent) are worth watching, but API-key avoidance and subagent routing should be evaluated for policy, provenance, and maintainability before being treated as durable tooling.

## Blind Spots

The missing category is governance for skills themselves. The week produced writing skills, slide skills, character-generation skills, offensive-security skills, and growth-hacking skills, but little visible work on signed skill manifests, sandboxed execution policies, dependency scanning for prompts and tools, or standardized audit logs.

Another gap is evaluation for long-horizon agent work. [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) and [waiterve/wai-play](https://github.com/waiterve/wai-play) point in the right direction, yet there is no broad surge in benchmarks that measure whether agents preserve intent, avoid reward hacking, or recover safely after partial failure. Physical AI is also underrepresented relative to press intensity; robotics, simulation assets, and autonomous-vehicle tooling did not show the same open-source breadth as agent workflows.

## The Week Ahead

Watch whether agent skills consolidate into trusted registries or keep spreading as ad hoc folders, prompt packs, and plugin bridges. Long-horizon harnesses should draw more attention if developers keep pushing agents into phones, browsers, office suites, and CLIs. The key question for next week is whether the ecosystem starts building the boring controls — signing, permissions, review units, and test harnesses — quickly enough to keep the skills economy from becoming another supply-chain mess.

## Key References

### Notable Projects

- [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) — The week’s strongest infrastructure signal because it treats long-running agent work as an audited, recoverable system.
- [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing) — A high-traction Chinese-language writing skill that shows the skills economy expanding beyond English coding workflows.
- [Binaryify/open-kimi-ppt-skill](https://github.com/Binaryify/open-kimi-ppt-skill) — A presentation-generation skill that mirrors the broader move of AI agents into office artifacts, despite its archived status.
- [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness) — A concrete example of agents reaching into mobile-device control, raising both usability and permissioning questions.
- [0xwilliamortiz/claude-red](https://github.com/0xwilliamortiz/claude-red) — Offensive-security skills packaged for Claude make the agent-skill supply-chain risk explicit.
- [jd-opensource/JoyAI-Video-Edit](https://github.com/jd-opensource/JoyAI-Video-Edit) — A substantial media-model repo that keeps AI video editing in the weekly signal set.
- [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) — Creative-production skills for coding agents reinforce the cross-language, cross-domain spread of reusable agent procedures.
- [n8n-io/n8n](https://github.com/n8n-io/n8n) — The large automation anchor showing why agent workflows are likely to converge with self-hosted integration platforms.
- [ollama/ollama](https://github.com/ollama/ollama) — The local-model anchor that keeps privacy, cost, and deployment control in the background of every agent discussion.

### Press & Industry

- [Cloudflare launches Kitesurf, a browser built for AI agents](https://techcrunch.com/2026/08/07/cloudflare-launches-kitesurf-a-browser-built-for-ai-agents/) — The clearest press-side signal that agent execution is moving into everyday application surfaces.
- [Turn one giant AI-generated pull request to a reviewable stack](https://github.blog/engineering/turn-one-giant-ai-generated-pull-request-to-a-reviewable-stack/) — GitHub’s practical answer to the review bottleneck created by cheap AI code generation.
- [The AI safety test is becoming a safety risk](https://techcrunch.com/2026/08/09/the-ai-safety-test-is-becoming-a-safety-risk/) — A useful counterweight to agent enthusiasm because it frames evaluation itself as an attack surface.
- [How we took malware advisories beyond npm](https://github.blog/security/supply-chain-security/how-we-took-malware-advisories-beyond-npm/) — Relevant because agent skills, MCP servers, and plugins increasingly resemble software supply-chain artifacts.
- [OpenAI acquires presentation startup NextSlide](https://techcrunch.com/2026/08/08/openai-acquires-presentation-startup-nextslide/) — A press-side marker for AI moving into office artifacts, echoed by slide and office-suite repos this week.
