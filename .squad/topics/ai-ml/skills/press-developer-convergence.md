# Skill: Press-Developer Convergence Detection

## Purpose
Identify weeks where press/industry coverage and developer activity converge on the
same theme, surfacing non-obvious editorial angles from the correlation.

## Method

### 1. Correlation Scan
Compare the week's press themes (from compact press-context artifact) against:
- New repo categories showing unusual growth
- Trending repos with thematic overlap to press narratives
- Community reaction repos (alternatives, self-hosted replacements, protest forks)

### 2. Convergence Strength Tiers

| Tier | Definition | Example |
|------|-----------|---------|
| **Strong** | Same-week developer repo response directly caused by press event | Copilot billing article → self-hosted AI workspace repos spike (W23) |
| **Meta** | Press narrative mirrors a pattern visible in developer metrics | Inflated AI ARR coverage ∥ star-inflation campaigns (W22) |
| **Weak** | Category overlap without causal link | General AI coverage + general AI repos trending |

### 3. Editorial Application
- **Strong convergence**: Lead with the narrative; developer data validates/extends press
- **Meta convergence**: Use as a thematic bridge; highlight the irony or structural parallel
- **Weak convergence**: Mention only if no stronger angle exists; caveat the correlation

## Reusable Patterns
- Platform billing/policy changes → monitor for self-hosting spikes within 7 days
- Acquisition announcements → watch for fork/migration activity in affected ecosystems
- Security disclosures → track patching velocity and alternative-tool adoption
- Regulatory announcements → observe compliance-tooling repo creation

## Quality Gate
- Never present correlation as causation without temporal evidence
- Always cite both the press source (URL, date) and the repo evidence (crawl data)
- Distinguish press-first (coverage preceded developer activity) from developer-first
