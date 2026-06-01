# Morbo's History

## Core Context
- **Project:** SquadScope (https://github.com/jmservera/SquadScope) — weekly editorial trend analysis of GitHub repos + tech press correlation
- **User:** jmservera
- **Created:** 2026-05-25
- **Stack:** Hugo static site deployed to GitHub Pages, custom design system in progress (Calculon's redesign — Phase 1 tokens shipped in #181, Phase 2 header/footer in flight as #171)
- **Live URL:** https://jmservera.github.io/SquadScope/
- **RSS:** https://jmservera.github.io/SquadScope/index.xml
- **Cadence:** Weekly publication (Mondays 08:30 UTC via crawl-and-publish workflow)

## Published so far
- W21 2026: "Agent Skills Go Mainstream While Star Farmers Game the Charts"
- W22 2026: "Supply-Chain Scanners, Skills Economies, and GitHub's Star-Farm Flood"

## Audience target
- Developers, tech leads, founders, investors who track open-source / AI trends
- Want signal vs noise on GitHub, not just "what's trending"
- Editorial weekly format — like a thoughtful Sunday read

## Distribution channels to consider
- Hacker News (Show HN for launch, then regular weekly post when story merits)
- Lobsters
- r/programming, r/dataisbeautiful, r/MachineLearning (where relevant)
- dev.to (full crosspost or summary)
- X / Bluesky / Mastodon thread per article
- LinkedIn (less developer-y but exec readership)
- Weekly newsletter (TBD: ConvertKit / buttondown / hand-rolled)
- GitHub README of SquadScope itself + topic listings
- Submit to "awesome-" lists when relevant (awesome-trending, etc.)

## Learnings

### Channel Fit Analysis (from #184 distribution strategy)

**High-priority channels (Week 1-4 focus):**
1. **Hacker News** — Best fit for SquadScope. Audience values signal/noise distinction and editorial judgment. Expect 30-80 upvotes, 500-2K CTR on launch. Rules: Post Wed/Thu 9:30-10 AM PST; "Show HN" only for launch; regular posts must feel like community contribution, not self-promo.
2. **Lobsters** — Strong secondary channel. Same audience as HN but smaller (1K-3K impressions). Better for follow-up discussions and niche topics (agent security, supply-chain tooling). Rules: Moderated well; community values depth.
3. **r/programming** — Third-tier consistency play. Bi-weekly max; respect community rules (no low-effort posts, engage in comments). 2K-8K impressions per post.

**Medium-priority channels (Week 2-4 expand):**
4. **Mastodon + Bluesky** — Thread format works well for SquadScope's analytical voice. Smaller absolute reach (300-2K impressions) but high-quality audience (FOSS practitioners, early adopters). Community-building focus over direct CTR.
5. **dev.to** — Crosspost with canonical URL to HN as primary distribution. Drives SEO juice back to site. 2K-8K impressions, modest but engaged audience.
6. **LinkedIn** — Broader but lower engagement. Angle toward tech leads + implications for hiring/org planning. 1K-5K impressions.

**Low-priority channels (defer or seasonal):**
- r/dataisbeautiful, r/MachineLearning: Use selectively when trends are viz-heavy or ML-focused
- Twitter/X: Saturated for trend content; lower signal/noise ratio than HN/Lobsters
- awesome-lists: One-time quarterly submission; high effort-to-reward ratio
- Newsletter (Buttondown): MVP phase; will scale with subscriber base

### Community Rules (Non-Obvious)

**HN-specific:**
- Post title must be neutral + specific ("Agent Skills Go Mainstream..." ✓, "GitHub Trends: You Won't Believe..." ✗)
- Story text should feel like a personal discovery, not a promotional blast
- Avoid posting same article twice in 2 weeks; violates unwritten norm, risks shadowban
- Optimal post time: Wed/Thu 9:30-10:30 AM PST (not Mon morning when everyone is active)

**Lobsters-specific:**
- Community is smaller, more moderated, more selective
- Self-posts ("I built X") appreciated more than link-shares
- Position as "analysis I wrote exploring GitHub trends" not "my trend service"
- Karma system discourages new accounts from posting; wait until account is 1-2 weeks old before heavy posting

**Reddit-specific:**
- r/programming auto-removes low-effort posts; must show genuine effort and community value
- Engage in comments; 80% of upvotes come from discussion, not title
- Max 1x per week per subreddit (unwritten rule; mods enforce)
- r/dataisbeautiful has stricter rules: data viz required, text-only analyses get deleted

**Mastodon/Bluesky-specific:**
- Thread format (5-7 toots) works better than single long-form posts
- Audience skews FOSS + privacy; avoid any mention of VC funding or commercial angle
- No direct link-through expected; focus is community building, not CTR
- Cross-instance federation means broader reach but slower engagement

### Effort-to-Reach Ratio & First 4 Weeks Allocation

Per-week effort: ~40-50 min of focused work (extract angles, draft posts, execute)

**Week 1 (Launch):**
- Focus: HN "Show HN" post + Mastodon thread
- Secondary: One r/programming post to test
- Effort: ~20 min post drafting + 10 min monitoring

**Weeks 2-4:**
- Establish cadence: HN (Wed), Mastodon (Mon), r/programming (Tue), LinkedIn (Tue), dev.to (Mon crosspost)
- Add: Lobsters (bi-weekly Fri)
- Monitor: CTR, engagement, sentiment per channel
- Adjust: If any channel underperforms, defer to monthly instead of weekly

### Blocking Dependencies

- SEO metadata audit (#187) must land before Week 1 launch posts go live (OG images need to be correct)
- GA4 (#182, #183) needed for accurate channel attribution by Week 4
