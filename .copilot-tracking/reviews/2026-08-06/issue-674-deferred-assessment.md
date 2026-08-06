<!-- markdownlint-disable-file -->

# Issue #674 Assessment — Post-Relaunch Feature Work

**Date**: 2026-08-06  
**Issue**: Repository Observatory: add to main nav, sort by mentions/stars, redesign repo page  
**Status**: OPEN, Deferred (P2 / Next Sprint)  
**Owner**: Amy (squad:amy)  
**Release**: backlog  

---

## Issue Summary

The Repository Observatory (`/repo/` section, 266 pages) is live and functional in production but has three UX gaps identified by sponsor (jmservera):

1. **Not discoverable**: No navigation link; must know URL to access
2. **Suboptimal sort**: Alphabetical by title; should sort by mentions or stars (engagement)
3. **Page design**: Single-repo page (layouts/repo/single.html) is functional but not well-designed

---

## Assessment vs. Phase 7 Acceptance Gates

**Critical Question**: Is Issue #674 blocking Phase 7 acceptance gates?

**Answer**: ❌ **No — Not a blocker**

**Reasoning**:
- Phase 7 gates: Timing (7.1), Security (7.2), Visual (7.3) acceptance
- Issue #674 scope: UX improvements, post-relaunch enhancement
- Release flags: Both disabled (`repo_pages.enabled = false`, `topic_hubs.dynamic_creation.enabled = false`)
- Feature status: Already live and working (pre-relaunch state, no regression)

**Impact**: Issue #674 can be deferred to post-relaunch without affecting release readiness.

---

## Scope Breakdown

### Work Item 1: Add `/repo/` to Main Navigation
- **File**: `hugo.toml` → `[menu.main]`
- **Complexity**: Low (5-10 minutes, one-liner)
- **Risk**: Low
- **Owner**: Amy
- **Success Criteria**: `/repo/` link appears in site header navigation with correct weight/placement

### Work Item 2: Change Repository List Sort Order
- **File**: `layouts/repo/list.html` (template change)
- **Options**: Sort by descending mentions (`distinct_weekly_issues`) or descending stars
- **Complexity**: Medium (requires PRD decision on sort criteria)
- **Risk**: Low
- **Dependencies**: Decision needed on sort order (mentions vs. stars)
- **Owner**: Amy (implementation) + jmservera (decision)
- **Success Criteria**: Repository list sorts by selected criteria (e.g., highest mentions first)

### Work Item 3: Redesign Single-Repo Page
- **File**: `layouts/repo/single.html` (template redesign)
- **Current Design**: Functional (description, GitHub link, weekly appearances, star-history table, tags, related repos, provenance)
- **Desired Design**: Better visual/UX presentation (card-based layout, hero section, chart treatment, etc.)
- **Complexity**: High (design-heavy, requires wireframing and CSS)
- **Risk**: Medium (visual regression risk, need visual testing)
- **Dependencies**: Design input (possibly from squad:calculon)
- **Owner**: Amy (with design input)
- **Success Criteria**: Redesigned page passes accessibility, performance, and visual regression tests

### Pre-Requisites
- [ ] PRD definition (decisions on sort criteria, page design direction)
- [ ] GitHub link preservation (must carry forward `.Params.repo_url` in any redesign)
- [ ] Lifecycle notices (archived/deleted banners must still render)
- [ ] Pagefind metadata (internal link contract from `scripts/check_internal_links.py` must remain valid)

---

## Definition of Done

**For BRD/PRD/Implementation**:
- [ ] BRD documents business rationale → `docs/brds/`
- [ ] PRD documents functional requirements → `docs/prds/`
- [ ] Implementation plan follows repo RPI tracking conventions
- [ ] Hugo build, internal-link check, existing test suites stay green
- [ ] Visual regression tests pass (if page design changed)

---

## Dependency on Phase 7 Gates

| Phase 7 Gate | Impact on #674 | Status |
|--------------|----------------|--------|
| 7.1 Timing | None | ⏳ In progress |
| 7.2 Security | None | ⏳ In progress |
| 7.3 Visual | None (separate visual suite) | ⏳ In progress |

**Conclusion**: Phase 7 completion does NOT unblock Issue #674 work. These are independent.

---

## When to Schedule

**Timeline Recommendation**:
- **Phase 7 Completion**: Expected 2026-08-09
- **Post-Relaunch Stabilization**: 2-3 days (2026-08-10 or later)
- **Issue #674 Start Date**: 2026-08-12 (next sprint, P2 priority)

**Rationale**: Allow 2-3 days post-relaunch for bug reports and stabilization before starting new UX work.

---

## Suggested Next Steps for Amy

1. **Post-Relaunch** (2026-08-10+):
   - Review sponsor feedback on current `/repo/` UX
   - Collaborate on PRD: sort criteria (mentions vs. stars)
   - Sketch single-repo page design (card layout, hero, charts, etc.)
2. **PRD Phase**: Document functional and design requirements
3. **Implementation**: Create BRD/PRD artifacts, schedule development
4. **Testing**: Update visual regression suite to cover redesigned pages
5. **Review**: Ensure GitHub link, lifecycle notices, Pagefind metadata all preserved

---

## References

**Issue**: github.com/jmservera/SquadScope/issues/674  
**Epic**: #594 (Claracle Data Observatory Relaunch)  
**Related Issues**: #602 (original repo pages build)  
**Dependencies**: #663, #664, #665, #666, #668, #669, #672, #673 (identity/lifecycle stabilization)

---

## Deferral Rationale

**NOT a blocker because**:
- Repository Observatory is already live (works today)
- Release flags remain disabled (feature not activated yet)
- Phase 7 acceptance gates focus on acceptance criteria, not new features
- UX improvements are additive (no regression risk to current state)

**Ideal timing**: Post-relaunch stabilization (2-3 days after Phase 7 closes)

---

## Status Summary

- **Phase 7 Impact**: ❌ None (independent)
- **Release Readiness Impact**: ❌ None (feature disabled)
- **Deferred to**: Post-relaunch (P2 next sprint)
- **Owner**: Amy (squad:amy)
- **Decision Owner**: jmservera (sort criteria, design direction)

