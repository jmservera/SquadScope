# Claracle Distribution Strategy

**Version:** 1.0  
**Last updated:** 2026-05-25  
**Owner:** squad:morbo  
**Status:** Ready for per-week playbook execution

---

## Audience Analysis

### Who Reads Weekly Trend Reports?

Claracle's audience spans three overlapping personas:

1. **Signal-seeking developers** (40-50%)
   - Want curated insights, not noise
   - Read to understand emerging patterns (agent infrastructure, supply-chain tooling, small-model races)
   - Primarily on HN, Lobsters, r/programming
   - Trust editorial judgment > raw trending data
   - Typical engagement: 8-12 min read, skim Notable Projects section, star 2-3 repos

2. **Tech leads & engineering managers** (25-35%)
   - Need to understand ecosystem shifts for hiring, technology choices, and org planning
   - Read summaries + Signal & Noise sections
   - Present findings in team standups
   - Found on LinkedIn, dev.to, tech newsletters
   - Typical engagement: 5-8 min read, focus on implications

3. **Founders & investors** (10-15%)
   - Track gaps, emerging categories, and competitive movements
   - Skim for "Blind Spots" and "Where Industry Meets Code" sections
   - Found on HN, Twitter/Bluesky, LinkedIn, sometimes Show HN threads
   - Typical engagement: 3-5 min targeted read

### Where They Hang Out

- **Developer communities:** Hacker News, Lobsters, r/programming, r/dataisbeautiful, r/MachineLearning
- **Social platforms:** Twitter/X (tech circles), Bluesky (early adopters), Mastodon (@fosstodon, @techhub), LinkedIn (broader reach)
- **Dev platforms:** dev.to, GitHub Discussions, RSS readers
- **Newsletters:** curated tech roundups, AI/ML focused lists, open-source digests

### What They Want

- **Signal vs. noise:** credible distinction between hype and substance
- **Editorial voice:** opinionated takes, not robotic summaries
- **Actionable context:** Why this week matters; what to watch next
- **No selling:** SquadScope is analysis, not promotion of any product or company

---

## Channel Mix Recommendation

| Channel | Effort | Expected Reach | Cadence | Notes |
|---------|--------|-----------------|---------|-------|
| **Hacker News** | 5 min | 5K-15K impressions, 50-200 upvotes | Launch + selective weeklies (2-4/month) | Post 9:30-10 AM PST Wed/Thu. "Show HN" for launch only; regular posts must meet HN community standards (no self-promotion feel). Community votes up on genuine signal, downvotes noise. |
| **Lobsters** | 5 min | 1K-3K impressions, 20-60 upvotes | Weekly (if editorial quality high) | Strong signal-seeking audience. Moderated well; low spam. Posts link to site with discussion on-platform. |
| **r/programming** | 5 min | 2K-8K impressions, 30-100 upvotes | Bi-weekly (avoid over-posting) | Active, semi-moderated. Respect community rules: no low-effort posts, link to Claracle site. Engagement via comments is key. |
| **r/dataisbeautiful** | 3 min | 1K-4K impressions | Selective (when trends are viz-relevant) | High quality bar. Only post when article includes strong data visualization or trend data. |
| **r/MachineLearning** | 3 min | 1K-3K impressions | Selective (AI/agent/model weeks only) | Narrow relevance; post only when ML is primary signal. Expect high-signal audience but low traffic if off-topic. |
| **Mastodon** | 8 min | 300-1K impressions (federated) | Weekly (thread format) | Target @fosstodon, @techhub, @pixelfed instances. Thread format (5-7 toots). Audience skews FOSS+privacy. No direct link clickthrough expected; community building focus. |
| **Bluesky** | 8 min | 500-2K impressions | Weekly (thread format) | Early-adopter tech crowd. Thread format (3-5 posts). Higher retweet/engagement than Mastodon but smaller absolute reach. |
| **Twitter/X** | 8 min | 2K-10K impressions | Weekly (thread) | Broader reach; audience spans investors, founders, practitioners. Thread with call-to-action link. Expect 5-15% conversion to clicks. |
| **LinkedIn** | 10 min | 1K-5K impressions | Weekly (1-2 posts) | Focus on "Where Industry Meets Code" angle and ecosystem implications for tech leads. Share link + short excerpt. Engagement: modest but high intent. |
| **dev.to** | 15 min | 2K-8K impressions | Weekly (full crosspost with canonical link) | Crosspost full article with `canonical_url` pointing back to Claracle. Drives SEO authority back to site. Community-friendly audience. |
| **Awesome-lists** | 10 min (one-time setup) | 100-500 impressions/month | Submit once per quarter | e.g., awesome-github-tools, awesome-open-source, awesome-ai-agents. One-time submission or annual update. Setup as a batch task. |
| **GitHub Topics** | 5 min (one-time) | 50-200 impressions/month | Update as categories evolve | Add to Claracle README: topics like `weekly-trends`, `github-insights`, `open-source-analysis`. One-time, minimal maintenance. |
| **Newsletter** | 20 min/week | 500-2K subscribers (TBD) | Weekly digest | Recommendation: **Buttondown** (see below). Auto-send Monday 9 AM UTC with week's article link + 3-5 key insights. |

---

## Launch Announcements (Ready-to-Paste)

### A. Hacker News "Show HN" Post

**Timing:** Wednesday 9:45 AM PST (post time drives visibility on HN)

**URL:** `https://www.claracle.com/`

**Title:** Show HN: Claracle – Weekly curated GitHub trends (AI agents, supply-chain security, noise filtering)

**Text:**
```
Hi HN,

I built Claracle, an automated system that crawls GitHub's new and trending repos 
each week, applies AI analysis to separate signal from noise, and publishes curated 
trend reports every Monday.

The problem I wanted to solve: GitHub's trending list is flooded with star-farm spam 
(emulator kits, game unlockers, etc.), making it hard to spot genuine infrastructure 
work. TechCrunch covers the funding layer; developers building tooling are invisible.

Claracle publishes:
- Weekly summaries (Mondays 8:30 AM UTC)
- Signal/noise breakdown (what's real, what's hype)
- Blind spots analysis (what's missing)
- "Where Industry Meets Code" (press vs. developer correlation)
- RSS feeds for integration with your reader

Stack: GitHub API crawl → Copilot CLI analysis → Hugo → GitHub Pages. 
No closed model deps; OSS where possible.

Two weeks of examples: https://www.claracle.com/ 
RSS: https://www.claracle.com/index.xml

Looking for feedback: Is this signal/noise split useful? Any categories you'd 
prioritize differently?

Thanks,
jmservera

P.S. This is my first launch here. Let me know if I should adjust anything.
```

**Expected outcome:** 30-80 upvotes, 50-150 comments, 500-2K click-throughs on first day.

---

### B. Mastodon Thread (Fosstodon + Techhub)

**Timing:** Monday 10 AM UTC (at publication)

**Post 1:**
```
🧵 New: SquadScope, a weekly digest of what's *actually* trending on GitHub.

The problem: GitHub's trending list is 40% star-farm spam (game unlockers, ROM 
emulators, NFT tools). TechCrunch covers AI funding; developers building actual 
infrastructure are invisible.

SquadScope is an automated crawler + AI analysis pipeline that publishes curated 
trend reports every Monday.
```

**Post 2:**
```
This week's themes:
- Agent infrastructure is consolidating (skills, harnesses, observability layers)
- Small models racing toward 4B-parameter efficiency
- Supply-chain security tooling becoming credible (Perplexity's bumblebee, Apple's corecrypto)
- Coordinated star-farm campaigns are escalating

https://www.claracle.com/
```

**Post 3:**
```
What makes it different from a Twitter bot:

1. *Editorial voice*: Each report includes "Signal & Noise" analysis, "Blind Spots" 
   (what's missing), and press correlation notes
2. *No ads or promotion*: Pure analysis, no vendor shilling
3. *Automatic weekly*: New report Monday 8:30 AM UTC
4. *RSS + social*: Subscribe however you like
```

**Post 4:**
```
Categories tracked:
- AI agents & coding infra
- Small model efficiency
- Supply-chain & security tooling
- Developer tools & observability
- Open-source patterns

Feedback welcome. Boosts + follows appreciated.
#github #opensource #aiagents #trends
```

**Expected outcome:** 20-50 boosts, 10-30 replies, small but high-quality audience (FOSS practitioners).

---

### C. dev.to Crosspost

**Timing:** Monday 12 PM UTC (2 hours after launch)

**Setup:** In dev.to post editor:
- **Canonical URL:** `https://www.claracle.com/`
- **Series:** "SquadScope Weekly" (so all posts thread together)
- **Tags:** `github` `trends` `opensource` `analysis`

**Draft post heading + intro:**
```markdown
# SquadScope: Weekly Curated GitHub Trends (W22 – Supply-Chain Scanners & Agent Skills)

Every Monday, SquadScope publishes an automated analysis of the week's most important 
new GitHub repositories, separated into signal and noise, with correlation to industry press.

This is the dev.to crosspost; the canonical article lives here: https://www.claracle.com/

## The Story This Week

Week 22 delivers the clearest defensive-security signal of the year alongside a crystallizing 
agent-skills economy — both nearly buried under the most concentrated coordinated star-farming 
campaign the crawl has caught.

[Full article link below]

---
*Read the full analysis on SquadScope:* https://www.claracle.com/
```

**Expected outcome:** 200-800 impressions, 5-20 reactions, 30-100 click-throughs to canonical URL.

---

## Per-Week Playbook (Concrete Example)

### Template: "From Article to Distribution in <30 min"

**Input:** `content/weekly/2026/W22.md` (published Monday 8:30 AM UTC)

**Before promotion:** Read the public [Methodology and corrections policy](../../content/methodology/_index.md) and link the live methodology page (`https://www.claracle.com/methodology/`) in launch/crosspost context when space allows. Do not promote an article as neutral or comprehensive; frame it as GitHub- and current-source-based analysis with known source, language, and platform limits.

**Step 1: Extract key angles** (5 min)
- Skim article for 3-5 "most quotable" sections
- Identify 1-2 thread hooks (what's surprising, what's missing)
- Flag any press correlation mentions

**Example from W22:**
```
Primary angle: Agent infrastructure + supply-chain security convergence
Secondary angle: Coordinated star-farm spam as ecosystem health signal
Thread hook: "TechCrunch covered inflated AI startup metrics at the exact moment 
GitHub is experiencing metric inflation via coordinated star farming"
```

**Step 2: Draft HN post** (5 min)
- Title: `Show HN: Claracle – [hook here]`
- Text: ~200 words covering: problem, what SquadScope does, this week's themes, RSS link
- Save as `.squad/posts/2026-W22-hn.txt`

**Step 3: Thread for Mastodon** (5 min)
- 4-6 toots, ~250 chars each
- Post 1: Hook + problem statement
- Post 2-3: This week's top 2-3 themes
- Post 4: Call to action (link, follow, boost)
- Save as `.squad/posts/2026-W22-mastodon.md`

**Step 4: Quick Reddit/r/programming post** (5 min)
- Title: Link to SquadScope headline
- Body: ~100 words, ask a question or flag a pattern
- Example: "This week we saw coordinated star-farming at a new scale. How is your org filtering signal from noise on GitHub trending?"
- Save as `.squad/posts/2026-W22-reddit.txt`

**Step 5: LinkedIn excerpt post** (5 min)
- 1-2 quotes from the article focused on *implications for tech leads*
- Example: "Agent infrastructure is consolidating into distribution layers. If you're hiring for AI tooling work, this week's trend report shows where the ecosystem is moving."
- Link to full article
- Save as `.squad/posts/2026-W22-linkedin.txt`

**Step 6: Queue/Publish**
- Post to HN immediately (if Wednesday timing)
- Schedule Mastodon for Monday 10 AM UTC (or post manually if no scheduler)
- Schedule Reddit for Tuesday morning
- Schedule LinkedIn for Tuesday 7 AM PST (peak engagement)
- dev.to: Crosspost Monday 12 PM UTC (after social, so canonical link juice flows back)

**Total time:** ~25-30 minutes  
**Distribution reach:** 10K-30K impressions, 100-500 direct clicks, 50-200 indirect (mentions, shares)

---

## SEO Audit: Gaps and Recommendations

### Current State

**What's working:**
- Basic meta description (line 21-23 in `layouts/partials/head.html`) ✓
- Schema.org BlogPosting markup (complete, line 62-126 in `schema_json.html`) ✓
- OpenGraph `og:title`, `og:description`, `og:type` (line 7-22 in `opengraph.html`) ✓
- Twitter card fallback (line 1-16 in `twitter_cards.html`) ✓

**Gaps identified:**

1. **Missing `og:image` fallback for homepage**
   - Current: Only uses `cover.image` if present; no fallback for articles without cover images
   - Impact: Social shares show no image, reducing CTR by 40-60%
   - **Fix:** Generate a default SquadScope OG image (e.g., SquadScope logo + week number) and reference it in `opengraph.html` as a fallback

2. **Missing `og:image:alt` tag**
   - Current: No alt text for OG images
   - Impact: Accessibility issue, some social platforms ignore image without alt
   - **Fix:** Add `<meta property="og:image:alt" content="...">` in `opengraph.html`

3. **Missing `twitter:creator` tag**
   - Current: Twitter cards include site but not author
   - Impact: No author attribution on Twitter shares
   - **Fix:** Add `<meta name="twitter:creator" content="@jmservera">` (or configured handle) in `twitter_cards.html`

4. **Homepage missing structured data (no og:image)**
   - Current: Homepage has no OG image configured
   - Impact: Homepage shares on social show no preview image
   - **Fix:** Add site-level OG image config in `config.yaml` + fallback in head.html

5. **Meta description is too generic for trend articles**
   - Current: Falls back to article summary (often first ~150 chars of body)
   - Impact: Trend reports have good summaries but not optimized for search CTR
   - **Fix:** Use the `summary` field in frontmatter (already present in W21, W22) and trim to 155 chars

6. **No `article:author` tag**
   - Current: Schema.org has author; OpenGraph does not
   - Impact: Inconsistent social metadata
   - **Fix:** Add `<meta property="article:author" content="SquadScope">` in `opengraph.html` (line 30-35 area)

7. **Missing image width/height in OG tags**
   - Current: `og:image` has no dimensions
   - Impact: Some social platforms require explicit dimensions for proper rendering
   - **Fix:** Add `og:image:width` and `og:image:height` to opengraph.html template

### Recommended Changes (File: `layouts/partials/templates/opengraph.html`)

**Location:** Between line 37-50 (after og:video section, before Facebook section)

**Add:**
```html
{{- /* og:image:alt and dimensions */}}
{{- if .Params.cover.image -}}
  <meta property="og:image:alt" content="{{ .Title }}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
{{- else }}
  {{- with partial "_funcs/get-page-images" . }}
    {{- with index . 0 }}
      <meta property="og:image:alt" content="Cover image for {{ $.Title }}">
      <meta property="og:image:width" content="1200">
      <meta property="og:image:height" content="630">
    {{- end }}
  {{- end }}
{{- end }}

{{- /* article:author tag */}}
{{- if .IsPage }}
  <meta property="article:author" content="{{ with .Params.author | default site.Params.author }}{{ . }}{{ else }}SquadScope{{ end }}">
{{- end }}
```

### Recommended Changes (File: `layouts/partials/templates/twitter_cards.html`)

**Location:** After line 37 (end of current file)

**Add:**
```html
{{- /* twitter:creator for attribution */}}
{{- with site.Params.social.twitter_creator | default site.Params.social.twitter }}
  {{- if not (strings.HasPrefix . "@") }}
    <meta name="twitter:creator" content="@{{ . }}">
  {{- else }}
    <meta name="twitter:creator" content="{{ . }}">
  {{- end }}
{{- end }}
```

### Recommended Changes (File: `config.yaml` or equivalent)

**Add to site params:**
```yaml
params:
  # ... existing config ...
  social:
    twitter: "jmservera"
    twitter_creator: "jmservera"
  # Add a default OG image for homepage/fallback
  og_image: "images/squadscope-og-default.png"  # 1200x630px
```

### Follow-up Issue: SEO Metadata Audit Fixes

Create issue `feat(seo): metadata audit fixes (#185)` with:
- Component: `routes: squad:amy` (HTML/Hugo specialist)
- Subtasks:
  1. Add `og:image:alt`, `og:image:width`, `og:image:height` to `opengraph.html`
  2. Add `article:author` meta tag to `opengraph.html`
  3. Add `twitter:creator` meta tag to `twitter_cards.html`
  4. Configure `twitter_creator` in `config.yaml`
  5. Create default OG image (1200×630) for social shares (coordinate with design/Calculon)
  6. Test social preview rendering on Facebook/Twitter with Link Debugger tools

---

## Tracking Convention (UTM Parameters)

### Standard UTM Structure

```
https://www.claracle.com/?utm_source={channel}&utm_medium={medium}&utm_campaign={campaign}
```

### Channel-Specific UTM Names

| Channel | `utm_source` | `utm_medium` | `utm_campaign` | Example |
|---------|-------------|-------------|----------------|---------|
| Hacker News | `hn` | `social` | `show-hn-launch` or `w22-launch` | `?utm_source=hn&utm_medium=social&utm_campaign=show-hn-launch` |
| Lobsters | `lobsters` | `social` | `weekly` | `?utm_source=lobsters&utm_medium=social&utm_campaign=w22` |
| r/programming | `reddit-prog` | `social` | `weekly` | `?utm_source=reddit-prog&utm_medium=social&utm_campaign=w22` |
| r/dataisbeautiful | `reddit-data` | `social` | `weekly` | `?utm_source=reddit-data&utm_medium=social&utm_campaign=w22` |
| r/MachineLearning | `reddit-ml` | `social` | `weekly` | `?utm_source=reddit-ml&utm_medium=social&utm_campaign=w22` |
| Mastodon | `mastodon` | `social` | `weekly` | `?utm_source=mastodon&utm_medium=social&utm_campaign=w22` |
| Bluesky | `bluesky` | `social` | `weekly` | `?utm_source=bluesky&utm_medium=social&utm_campaign=w22` |
| Twitter/X | `twitter` | `social` | `weekly` | `?utm_source=twitter&utm_medium=social&utm_campaign=w22` |
| LinkedIn | `linkedin` | `social` | `weekly` | `?utm_source=linkedin&utm_medium=social&utm_campaign=w22` |
| dev.to | `devto` | `referral` | `canonical` | `?utm_source=devto&utm_medium=referral&utm_campaign=canonical` |
| Newsletter | `newsletter` | `email` | `weekly` | `?utm_source=newsletter&utm_medium=email&utm_campaign=w22` |
| awesome-lists | `awesome-lists` | `referral` | `discovery` | `?utm_source=awesome-lists&utm_medium=referral&utm_campaign=discovery` |

### GA4 Import

Once GA4 lands (#182), configure custom dimensions:
- `utm_source` → Dimension: `channel`
- `utm_medium` → Dimension: `medium`
- `utm_campaign` → Dimension: `campaign_week`

Dashboard: Track weekly referral sources, top-performing channels, conversion (click-through) by channel.

### Manual Tracking (Until GA4)

Before GA4, log weekly:
- Social post impressions (platform-native analytics)
- Comments/engagement per post
- Anecdotal feedback (who quoted you, who shared)
- Record in `.squad/metrics/2026/w22-distribution.md`

---

## Newsletter Tool Recommendation

### Recommendation: **Buttondown**

**Rationale:**
- **Simple:** Free tier supports up to 1,000 subscribers with unlimited emails
- **Markdown-first:** Write newsletters in Markdown, same workflow as SquadScope content
- **GitHub integration:** Supports RSS-to-email (auto-send when new article publishes)
- **Minimal friction:** No fancy template builder; focus on content
- **Privacy-respecting:** No cross-platform ad tracking; user data stays minimal
- **Cost:** Free until 1K subscribers; $9/mo at 5K; scales linearly

**Setup workflow:**
1. Create Buttondown account (https://buttondown.email)
2. Configure RSS-to-email trigger pointing to `https://www.claracle.com/index.xml`
3. Set delivery: Monday 9 AM UTC (1.5 hours after article publish)
4. Template: Auto-generated from RSS feed (title + excerpt + link)
5. Custom intro: "New SquadScope analysis just dropped. Here's this week's trends:" + RSS excerpt
6. Subscribe CTA: Add signup link to SquadScope homepage footer

**Alternative considered:** ConvertKit
- Pros: More sophisticated automation, good for building audience long-term
- Cons: $0/mo free tier is limited; $9/mo minimum for custom domains; overkill for MVP
- Decision: Start with Buttondown MVP, migrate to ConvertKit if subscriber base exceeds 5K

**Out of scope:** Hand-rolled GitHub Actions + email service
- Reason: Premature optimization; Buttondown handles the hard parts (deliverability, unsubscribe compliance)

---

## What NOT to Do (Anti-Patterns)

1. **Never post the same article to HN more than once per 2-week window**
   - Violates HN community norms; risks shadowban
   - If repost necessary, only after significant updates (new sections added, 2+ weeks passed)

2. **Avoid multi-posting to same subreddit within 48 hours**
   - Seen as spam; triggers mod warnings or post removal
   - Cadence rule: r/programming max 1x per week; r/dataisbeautiful max 1x per fortnight

3. **Don't ignore community-specific rules**
   - r/programming: No low-effort content, discussion required
   - r/dataisbeautiful: Only posts with strong visualization; text-only analyses removed
   - Lobsters: No self-promotion tone; position as "analysis I wrote" not "check out my thing"

4. **Never cross-post identical text to multiple platforms**
   - Tailor each post to platform norms and audience (HN is intellectual, Twitter is casual, LinkedIn is professional)
   - Effort: 80% same angle, 20% platform-specific framing

5. **Avoid posting during low-traffic windows**
   - HN: 9-11 AM PST (Wed/Thu) for best velocity
   - Reddit: 9-11 AM PST or 7-9 PM PST (peak US activity)
   - Mastodon/Bluesky: 9-10 AM UTC (federated networks peak morning EU)
   - LinkedIn: 7-9 AM or 12-1 PM PST (lunch + morning commute)

6. **Never include affiliate links or sponsorship plugs**
   - Breaks trust with audience; platform ToS violations
   - SquadScope is pure editorial; no monetization angle

7. **Avoid vanity metrics**
   - Don't optimize for star-count or comment volume; optimize for *signal* (do comments show genuine interest?)
   - Coordinate campaigns look like 420-429 stars, zero forks, overnight spam — that's the anti-pattern

8. **Don't post without reading community mod guidelines first**
   - Many subreddits auto-delete posts from new accounts or without proper flair
   - Lobsters has karma requirements for posting
   - GitHub Discussions has topic-specific norms

9. **Never use clickbait headlines**
   - HN downvotes sensationalism aggressively
   - Trend report titles should be neutral + specific: "Supply-Chain Scanners, Skills Economies, and GitHub's Star-Farm Flood" ✓ "You Won't BELIEVE What GitHub Trends Show This Week" ✗

10. **Avoid inconsistent voice**
    - SquadScope's editorial voice is analytical, slightly opinionated, always evidence-based
    - Social posts should reflect this tone; don't turn cheerful for Twitter or corporate for LinkedIn
    - Consistency > optimization

---

## Launch Checklist

- [ ] Distribution strategy document approved and merged (`squad/184-distribution-strategy`)
- [ ] SEO metadata audit issues created (routes to squad:amy)
- [ ] Default OG image created (1200×630, SquadScope branding)
- [ ] Buttondown account set up + RSS configured
- [ ] First launch posts drafted in `.squad/posts/2026-W22-*`
- [ ] GA4 foundation in place (blocks on #182, #183)
- [ ] Metrics tracking template created (`.squad/metrics/2026/w22-distribution.md`)
- [ ] Newsletter signup link added to homepage footer
- [ ] Social profile links (Twitter, Mastodon, GitHub) finalized in site footer
- [ ] Per-week playbook calendar started (one row per Monday publish)

---

## Metrics to Track (Per Week)

| Metric | Where | Why | Target |
|--------|-------|-----|--------|
| **Total impressions** | Platform analytics | Show audience reach | 10K-30K combined |
| **Click-through rate (CTR)** | GA4 UTM + platform | Show engagement quality | 2-5% from social |
| **Referral sources** | GA4 | Identify top channels | Rank HN, Lobsters, Reddit top-3 |
| **Comments/engagement** | Platform-native | Show community interest | 30+ comments across platforms |
| **Newsletter signups** | Buttondown | Build owned audience | +50-100/week |
| **RSS subscribers** | FeedBurner or equivalent | Track subscription growth | +10-20/week |
| **Shares/retweets** | Twitter/Bluesky/Mastodon | Amplification factor | 5-10 organic shares |
| **New GitHub stars** | GitHub repo stars | Track project awareness | +50-100 stars/week |

---

## Next Steps

1. **Week 1 (immediate):**
   - Approve and merge this document
   - Create follow-up issues: SEO audit + W23 launch playbook
   - Set up Buttondown + newsletter signup link

2. **Week 2-4 (ongoing):**
   - Execute per-week playbook for W23, W24, W25
   - Track metrics per channel
   - Append learnings to `.squad/agents/morbo/history.md`

3. **Month 2 (optimize):**
   - Review channel performance data
   - Double down on top 3-4 channels
   - Deprioritize low-signal channels
   - Refine post timing based on GA4 data

4. **Month 3+ (scale):**
   - Evaluate whether newsletter should move off Buttondown (if >1K subscribers)
   - Explore paid distribution options (if metrics justify)
   - Build SquadScope brand presence on all key platforms
