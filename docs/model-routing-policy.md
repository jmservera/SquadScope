# SquadScope Model Routing Policy

**Effective:** 2026-06-06  
**Issue:** #273  
**Status:** Team Policy

## Executive Summary

This policy defines when SquadScope agents use expensive high-reasoning models (GPT-5.5, GPT-5.3-Codex, Claude Opus) vs. cost-effective models (Claude Haiku, GPT mini). The goal is to **maximize value per dollar** by reserving premium models for work requiring high-quality reasoning, while keeping routine tasks efficient.

**Governing principle:** Cost first, **unless code is being produced**. Visual/design work always uses premium vision-capable models. Cross-family review assignments reduce correlated blind spots.

**Pricing source:** [GitHub Copilot Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), fetched 2026-06-06. Pricing assumptions must be reviewed every two months.

The scheduled workflow `.github/workflows/copilot-pricing-review.yml` runs every two months to open or update a review issue when the table is due. It is notification-only and must not change pricing data without a PR.

---

## Model Selection Hierarchy

The model selection process follows a 6-layer hierarchy (Layers 0–5 plus fallback chains). The first matching layer wins.

### Layer 0: Persistent Configuration

Read `.squad/config.json` on every session start:

```json
{
  "version": 1,
  "defaultModel": "claude-sonnet-4.6",
  "agentModelOverrides": {
    "leela": "claude-opus-4.5",
    "fry": "claude-haiku-4.5"
  }
}
```

- **`defaultModel`:** Applied to all agents unless overridden. Persists across sessions.
- **`agentModelOverrides`:** Agent-specific overrides. Typed as `{agentName: modelString}`.
- **Update when:** User says "always use X" or "use X for {agent}". Save once, apply always.

### Layer 1: Session Directive

Did the user specify a model for **this session only**? Examples:
- "Use GPT-5.5 for this task"
- "Cut costs — use Haiku for everything today"
- "Run a code review with Opus"

Session directives persist until the session ends or are contradicted. They take precedence over persistent config.

### Layer 2: Charter Preference

Does the agent's charter (in `.squad/agents/{name}/charter.md`) contain a `## Model` section with `Preferred: {model}`?

Example:
```markdown
## Model

Preferred: claude-opus-4.5
Rationale: Leela's reviews require sophisticated code analysis.
```

If yes, use that model unless overridden by Layers 0 or 1.

### Layer 3: Task-Aware Auto-Selection

If no override was specified, **determine the task output type** and select accordingly:

#### Code or Technical Implementation

**Output type:** Produces code files, code reviews, architecture diagrams, complex technical documentation  
**Model selection logic:**

- **Heavy code generation (500+ lines or multi-file refactor)** → `gpt-5.3-codex` or `claude-sonnet-4.6` (highest code quality)
- **Standard code tasks** → `claude-sonnet-4.6` (balance of quality and speed)
- **Simple scaffolding or boilerplate** → `claude-haiku-4.5` (cost-effective for mechanical code)

#### Non-Code (Docs, Planning, Analysis, Triage, Logs)

**Output type:** Markdown docs, decision logs, planning docs, test case definitions, changelog entries, operational reports  
**Model selection:** `claude-haiku-4.5` (cost wins when code is not produced)

#### Visual / Design Work

**Output type:** Image analysis, UI/UX feedback, design evaluation, visual accessibility  
**Model selection:** `claude-opus-4.5` (vision capability required; never downgrade)

### Layer 4: Role-to-Model Mapping

When task-aware selection is active, use this table to resolve defaults for each role:

| Role | Default Model | Why | Exceptions |
|---|---|---|---|
| **Core Dev / Backend / Frontend** | `claude-sonnet-4.6` | Writes code — quality first | Heavy code gen (500+ lines) → `gpt-5.3-codex` |
| **Tester / QA** | `claude-sonnet-4.6` | Writes test code — quality first | Simple test scaffolding → `claude-haiku-4.5` |
| **Lead / Architect** | *per-task* | Mixed: code review needs quality, planning needs cost | See task-aware rules above |
| **Prompt Engineer** | *per-task* | Prompt design ≈ code work; research is not | Prompt architecture → `claude-sonnet-4.6`; research → `claude-haiku-4.5` |
| **Copilot SDK Expert** | `claude-sonnet-4.6` | Technical analysis often touches code | Pure research → `claude-haiku-4.5` |
| **Designer / Visual** | `claude-opus-4.5` | Vision required; never downgrade | — |
| **DevRel / Writer** | `claude-haiku-4.5` | Docs and writing — not code | — |
| **Scribe / Logger** | `claude-haiku-4.5` | Mechanical file ops — cheapest possible | — |
| **Git / Release** | `claude-haiku-4.5` | Mechanical ops (changelogs, tags, version bumps) | — |

### Layer 5: Fallback Chains

If a selected model is unavailable (plan restriction, deprecation, rate limit, org policy), **retry with the next model in the chain**. When degrading from a requested model, acknowledge the change to the user (see **User notification** guidance in Handling Unavailability section below).

**Fallback chains (in priority order):**

**Premium chain (Opus/high-reasoning):**
```
claude-opus-4.6 → claude-opus-4.5 → claude-sonnet-4.6 → claude-sonnet-4.5 → (omit model)
```

**Standard chain (Sonnet/mid-tier):**
```
claude-sonnet-4.6 → claude-sonnet-4.5 → gpt-5.4 → gpt-5.3-codex → claude-sonnet-4 → (omit model)
```

**Fast chain (Haiku/budget):**
```
claude-haiku-4.5 → gpt-5.4-mini → gpt-5-mini → gpt-5.4-nano → (omit model)
```

`(omit model)` = Call the tool without the `model` parameter. The platform default applies (nuclear fallback — always works).

**Fallback rules:**
- If user specified a provider (e.g., "use Claude only"), fall back within that provider only
- Never fall back **up** in tier — a fast task should not land on a premium model
- Log fallbacks to `.squad/orchestration-log/` for debugging, but don't surface to user unless asked
- Maximum 3 retries before hitting nuclear fallback

---

## When to Use GPT-5.5

> **Note:** GPT-5.5 is referenced in the model recommendations as a high-cost/high-reasoning choice. Availability varies by Copilot surface and plan (see **Caveats** section below).

### Justified Use Cases

GPT-5.5 is justified when **all** of the following hold:

1. **High-reasoning/editorial judgment required:**
   - Architectural decisions for multi-agent coordination
   - Code reviews where subtle logic errors could have high impact
   - Security audits and vulnerability assessment
   - Editorial policy decisions for SquadScope (e.g., what constitutes "signal" vs. "noise")

2. **Output feeds 3+ downstream agents or components:**
   - A decision made by this agent enables or blocks work for multiple teams
   - Example: Lead architecture proposal → informs 4 dev team implementations

3. **Cost is secondary to quality:**
   - The cost of a mistake (slow rework, security issue, architectural debt) exceeds the model cost delta

### Not Justified

GPT-5.5 is **not** justified for:
- Routine code scaffolding or boilerplate generation
- Single-file bug fixes or typo corrections
- Data transformation, JSON parsing, or mechanical renames
- Content generation where quality is "good enough" (not requiring highest judgment)
- Any task where the output is disposable (e.g., draft planning docs that will be replaced)

### Mandatory Restrictions

- **Never use GPT-5.5 for:** Scribe/logging tasks, changelog generation, version bumps, or any mechanical operation
- **Never cascade:** Only one agent per workflow should use GPT-5.5. If two agents in the same workflow both need high reasoning, use GPT-5.5 for the one that feeds the other (upstream agent wins)

---

## Cross-Family Code Review & Rubber-Duck Rules

### When to Use Cross-Family Review

Use agents from **different model families** (Claude vs. GPT vs. Gemini) when reviewing code to reduce correlated blind spots.

**Definition of families:**
- **Claude family:** Claude Opus, Claude Sonnet, Claude Haiku
- **GPT family:** GPT-5.x, GPT-4.x, GPT mini
- **Gemini family:** Gemini Pro, Gemini Flash

### Review Assignment Policy

For code reviews and security audits, assign reviewers as follows:

1. **Primary reviewer:** Lead or QA agent (per charter; typically highest-reasoning model available)
2. **Cross-family reviewer:** Agent from a different family as the primary
   - If primary is Claude Sonnet → secondary is GPT-5.3-Codex or Gemini Pro
   - If primary is GPT-5.3-Codex → secondary is Claude Sonnet or Gemini Pro
   - If primary is Gemini → secondary is Claude Sonnet or GPT

**Example workflow:**
```
1. Leela (Claude Opus) performs primary code review → finds X, Y, Z issues
2. Fry (GPT-5.3-Codex) performs cross-family review → catches W issue (correlated blind spot)
3. Result: Combined coverage X, Y, Z, W
```

### Rubber-Duck Reviews (Lightweight)

For lightweight code clarity reviews or rubber-duck debugging:
- Use any available model from a **different family** than the code author
- No need to bump to premium if the primary reviewer already covered quality gates
- Example: Fry wrote the code in `claude-sonnet-4.6` context → Farnsworth (Gemini Flash) does rubber-duck for fresh perspective

### When Cross-Family Is Not Required

- Single-developer features with no security implications
- Internal helper functions or tests (lower risk)
- Mechanical changes (renames, version bumps, boilerplate)
- Documentation-only changes

---

## Model Availability & Caveats

### By Copilot Surface

**GitHub Copilot CLI (command line):**
- All models in standard/fast chains available
- Premium (Claude Opus, GPT-5.5) available if user has Copilot Pro or Business plan
- Haiku and mini models always available

**GitHub Copilot in VS Code:**
- Standard models available (Claude Sonnet, GPT-5.x)
- Premium limited by plan
- Check VS Code market for current availability

**GitHub Copilot Chat (web):**
- Limited model availability
- Premium/reasoning models may be restricted to Copilot Pro users

**GitHub Copilot Coding Agent (cloud autonomous agent mode):**
- Model availability may differ from CLI/Chat depending on cloud agent configuration and plan
- Some models may have per-session or per-day limits
- Consult your cloud agent provisioning docs for availability specifics

### By Organization Plan

| Plan | Models Available | Restrictions |
|---|---|---|
| **Free / Community** | Haiku, GPT mini | No Sonnet or premium; may have rate limits |
| **Copilot Free** | Haiku, GPT mini, Sonnet | No premium (Opus, GPT-5.5); limited requests |
| **Copilot Pro** | All models | Full access; may have per-session limits |
| **Copilot Business** | All models (enterprise rate limit pool) | Full access; shared rate limits per org |
| **GitHub Models API** | Limited pool per provider | Check `models-health` artifact before runs |

### Handling Unavailability

1. **Preflight check:** Before expensive runs, verify model availability via `models-health` check or test call
2. **Fallback chain:** Use the fallback chain defined above (Layer 5) when a model is unavailable
3. **Degradation logging:** Log degradation to `.squad/orchestration-log/` for audit trail
4. **User notification:** If a task must degrade from requested model, acknowledge: *"Using {fallback_model} — {primary_model} unavailable on current plan."*

### Plan-Specific Guidance for SquadScope

**SquadScope weekly analysis runs on:** GitHub Actions with Copilot CLI. GitHub Models/OpenAI fallback is not configured for analysis; Copilot failures fail closed or produce publish-ineligible diagnostic artifacts for operator triage.
**Assumed availability:**
- Claude Sonnet 4.6, Claude Haiku 4.5
- GPT-5.3-Codex, GPT-5.4, GPT-5.4 mini, GPT-5 mini
- Gemini 3.1 Pro, Gemini 3 Flash, Gemini 3.5 Flash

**High-cost operations** (analysis, reskill, complex code reviews):
- Check model availability before spawning
- Prefer Haiku for routine map/reduce tasks
- Use Sonnet for code writing; reserve Opus/GPT-5.5 for judgment calls only

---

## Configuration Examples

### Example 1: Cost-Focused Config

```json
{
  "version": 1,
  "defaultModel": "claude-haiku-4.5"
}
```

All agents default to Haiku unless overridden by task type or charter.

### Example 2: Premium-Biased Config (for editorial/reasoning work)

```json
{
  "version": 1,
  "defaultModel": "claude-sonnet-4.6",
  "agentModelOverrides": {
    "leela": "claude-opus-4.5",
    "fry": "gpt-5.3-codex"
  }
}
```

Leela (Lead) and Fry (code reviewer) get premium; others get Sonnet.

### Example 3: Mixed Config (typical for SquadScope)

```json
{
  "version": 1,
  "defaultModel": "claude-sonnet-4.6",
  "agentModelOverrides": {
    "bender": "claude-opus-4.5",
    "scribe": "claude-haiku-4.5",
    "ralph": "claude-haiku-4.5"
  }
}
```

Developers (Bender) and decision-makers (Leela/implicit) get Sonnet; review/coordination (Bender with Opus for complex reviews) gets premium; logging/monitoring (Scribe/Ralph) always budget.

---

## Decision Log & Rationale

### Principle: Cost First, Unless Code

Copilot compute cost is measured per token and model tier. Within the same session:
- Deploying Opus instead of Sonnet costs ~3-4x more per token
- For non-code tasks (docs, planning, logs), token count is low → cost difference is negligible, but quality difference is also negligible
- For code tasks, quality difference is material (fewer bugs, better architecture) and value of better code > cost delta

**Decision:** Haiku for all non-code. Sonnet/Codex for code. Opus/GPT-5 only for high-judgment work that feeds downstream decisions.

### Principle: Cross-Family Review Reduces Correlated Blind Spots

Research in model behavior shows that different model families (Claude, GPT, Gemini) have different strengths:
- Claude excels at structured reasoning and following complex constraints
- GPT excels at diverse patterns and few-shot adaptation
- Gemini excels at multimodal tasks and certain low-resource languages

**Decision:** Major code reviews and security audits should use 2 reviewers from different families. This catches blind spots unique to any single family.

### Principle: Rubber-Duck Is Cheap

Rubber-duck reviews (explaining code to catch logic errors) benefit from:
- A fresh perspective (different agent, different training)
- Lower consequence (it's not a gate, just a check)
- High review velocity (ask all available reviewers)

**Decision:** Assign rubber-duck reviews to any available model from a different family. No need to bump to premium.

### Principle: Editorial Judgment Requires Premium

SquadScope's weekly analysis applies editorial judgment (signal vs. noise, trend significance). This judgment:
- Affects downstream publication and reader trust
- Cannot be easily validated or corrected
- Benefits from highest-reasoning capability

**Decision:** Use GPT-5.5 or Claude Opus for analysis decisions that become published content. Use Sonnet for draft versions and candidate analysis. Use Haiku for data transformation and boilerplate only.

---

## FAQ

### Q: Can I force a specific model for all my work?

**A:** Yes. Set `defaultModel` in `.squad/config.json`, or specify a session directive ("use GPT-5.5 for this session"). The Lead can also update agent charters to pin specific models to specific agents.

### Q: What if my org doesn't have access to GPT-5.5?

**A:** Use the fallback chain. If GPT-5.5 is unavailable, it will fall back to `claude-sonnet-4.6` or `gpt-5.3-codex`. You'll get slightly lower quality but the same output type. Check `.squad/orchestration-log/` to see which model was actually used.

### Q: Should I always use premium for code reviews?

**A:** No. Use premium (Opus/GPT-5.5) for code reviews when:
1. The code impacts security or architectural stability, OR
2. The code feeds downstream work for 3+ agents, OR
3. You explicitly want cross-family review
Otherwise, Sonnet is sufficient for routine PRs.

### Q: Can I use different models for the same agent on different days?

**A:** Yes. Session directives override persistent config. If you say "use Haiku today", it applies for this session only. The persistent config resumes tomorrow. Temporary overrides don't require config changes.

### Q: How do I know if a model is available?

**A:** Check your Copilot surface docs or contact your account manager:
- **CLI users:** Run `gh copilot models list` to see available models on your plan
- **VS Code users:** Check the model selector in the Copilot Chat interface
- **GitHub Models API users:** Consult the GitHub Models availability page for current supported models
- **Business/Enterprise:** Contact your GitHub account team for plan-specific model access

---

## Approval & Governance

**Owner:** Lead Architect (Leela)  
**Last Updated:** 2026-06-06  
**Review Cycle:** Every two months for pricing assumptions (next: 2026-08-06); broader routing policy quarterly.
**Changes Require:** Issue + consensus from development team  

This policy is **descriptive** (documents current practice) and **prescriptive** (governs future decisions). Changes to this policy should be reflected in both `.squad/config.json` (if persistent config changes) and this document (for governance/principle changes).
