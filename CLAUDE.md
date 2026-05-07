# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- **Research → Plan → Implement, in that order.** Every task starts with reading the relevant code and writing a brief plan. No direct implementation without understanding the problem first. The output of research and planning lands in [TASKS.md](TASKS.md) — see "Task Discipline" below.
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Task Discipline

**Track work in [TASKS.md](TASKS.md). Lifecycle: Research → Planned → In-Progress → Done.**

- TASKS.md is the single source of truth for in-flight and queued work. Open it at the start of every session; close out work in the same commit that ships the code.
- When you discover an issue, limitation, or gap mid-task, log it in TASKS.md ("Issues / Technical Debt") **before context-switching**. Don't trust memory.
- Speculative ideas go to "Research / Ideas". Promote to "Backlog" only after a brief research pass clarifies scope and acceptance criteria.
- Cap "In Progress" at 2. More than that means you're not finishing things.
- Challenge existing implementations when you touch them — note debt or improvement candidates in TASKS.md instead of silently rewriting.

## 6. Documentation & Tracking Consistency

**Documentation is part of the feature. Ship it in the same commit as the code.**

After any **major change**, review and update — in the same commit as the code change:

- [CLAUDE.md](CLAUDE.md) — when workflows, conventions, architecture, or runtime behavior change.
- [README.md](README.md) — when setup, usage, public-facing features, env vars, or endpoints change.
- [TASKS.md](TASKS.md) — move the completed task to "Completed", log newly discovered issues to "Issues / Technical Debt", and queue follow-ups to "Backlog".

**What counts as a major change:**
- New feature or endpoint.
- Architecture or pipeline modification.
- New integration (service, library, external dependency).
- Refactor that moves code across modules or changes a public contract.
- Any change in observable system behavior, performance characteristics, or operational defaults.

**Enforcement:**
- If a file does not need an update, state explicitly which files you reviewed and why no change was required. Silent skips are not acceptable.
- The three files must stay consistent with each other: a fact stated in one must not contradict another.
- A change that ships code without the matching doc update is incomplete. Treat the doc lines as part of the diff, not an afterthought.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Workflow

- For commands that take a long time to run (build steps, ingestion scripts, docker builds, etc.), tell the user what to run instead of executing them directly. The user will run them manually.
- After each implementation, test what has been done (run relevant tests, hit the endpoint, verify the behavior).
- For documentation/tracking updates after a change, follow section 6 ("Documentation & Tracking Consistency").

## 7. Project Guards (DzTherapy-specific, locked invariants)

These are non-negotiable for DzTherapy. Every suggestion must respect them.

1. **No per-session commission, ever.** Locked by business model. Even small "convenience fees" are off the table — breaking the "we never take a cut of your sessions" promise to therapists destroys trust and the company.
2. **Therapist-first filter.** Every product/feature suggestion must pass: *"does this make therapists more likely to subscribe in year 2?"* If a feature only helps users without strengthening therapist stickiness, it's a luxury this bootstrapped runway can't afford.
3. **Pass-through payments only at MVP.** The platform never holds or processes user→therapist money. Therapists publish their own payment instructions (CCP/RIB/Edahabia); users pay them directly off-platform. This avoids SATIM merchant onboarding, PSP licensing, KYC and fraud liability.
4. **Bootstrap constraints are real.** Default to free hosting/email/video tiers, no paid tools, no salaries. Years 1–2 have zero revenue by design — every avoidable cost shortens the path to dying.
5. **French-only UI at MVP.** Arabic in Phase 2, English Phase 3+. Don't proactively suggest multi-language work for v1.

## 8. Project State and Source of Truth

- **DzTherapy is pre-code as of 2026-05-07.** No application has been built yet. The folder contains: this `CLAUDE.md`, the PRD ([algeria_mental_health_saas_prd.md](algeria_mental_health_saas_prd.md)), [TASKS.md](TASKS.md), and [README.md](README.md).
- **The PRD is the source of truth** for product strategy, business model, MVP scope, roadmap, risks, and validated/unvalidated assumptions. Read it before suggesting features or making architectural decisions.
- **When code scaffolding begins, this file gains:** a "Running" section (build / dev / test commands), an "Architecture" section (modules, request flow, external dependencies), and "Conventions" specific to the chosen stack.
- **Tentative tech stack** (from PRD §13, subject to change once a stack decision is locked):
  - Frontend: Next.js + TailwindCSS on Vercel free tier
  - Backend: Next.js API routes OR FastAPI — decide once based on team skill
  - Database: PostgreSQL on Supabase or Neon free tier
  - Video: Daily.co free tier
  - Email: Resend or Postmark
  - Single monolith. **No** Redis / WebSockets / Kubernetes / React Native at MVP.
