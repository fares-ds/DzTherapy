# Product Requirements Document (PRD)
## Algerian Mental Health SaaS Platform — *DzTherapy*

> **Version 2 — pressure-tested rewrite.** Changes from v1: business model clarified (no per-session commission, ever — therapist subscription in year 2 only), MVP scope cut by ~70%, payments reframed as pass-through (no PSP role), risks re-prioritized around runway, and a new Validated vs Unvalidated Assumptions appendix added.

---

# 1. Executive Summary

## Strategic thesis
DzTherapy is a **two-sided platform with a one-sided revenue model**:
- **Years 1–2 (free phase):** A user-facing marketplace that connects Algerians with verified therapists. Free for users, free for therapists, and the platform takes **0% commission** on sessions. Users pay therapists directly, off-platform.
- **Year 2+ (monetization phase):** Therapists pay a **monthly SaaS subscription** for the tools and the lead flow they have been using for free. This is the **only** revenue stream. Per-session commission is explicitly off the table, forever.

**Why this works:** the user-side marketplace is not a revenue product — it is a *customer acquisition funnel for the therapist SaaS*. Every user who books through DzTherapy is a billable session of value being delivered to a therapist who, in 18 months, will have a calendar full of platform-sourced clients and will pay to keep that flow alive.

## Measurable definitions
- **Accessible** = bookable in <60 seconds from any smartphone, including on 3G connections.
- **Private** = no public profile required, anonymous display name option in Phase 2, encrypted-in-transit communications, no payment data held by platform.
- **Affordable** = sessions delivered at 1,500–3,500 DZD (today's typical urban clinic rate is ~3,500–5,000 DZD).
- **Culturally adapted** = same-gender filter, French + Arabic UI, "wellness" framing in copy (not "therapy"), avoidance of stigmatized clinical language in marketing.

## Why now
Three things converge in Algeria today: (a) post-COVID legitimization of video consultation, (b) a critical mass of psychologists with smartphones and patient WhatsApp groups but no booking infrastructure, and (c) the rising mental-health awareness of the under-35 cohort driven by social media. None of these were true 5 years ago.

---

# 2. Problem Statement

> Each item below is tagged as `[validated]` (we have evidence) or `[assumption]` (we believe it, but it needs research before launch). See §22 for the full assumptions appendix.

## User problems
- Difficulty finding trusted therapists `[assumption]`
- Social stigma around therapy `[assumption — directionally true, magnitude unknown]`
- Limited access outside major cities `[validated — geographic distribution of registered psychologists]`
- No digital booking systems in most clinics `[validated]`
- Limited online payment adoption `[validated]`
- High friction for first-time users (cold-calling clinics, gendered awkwardness) `[assumption]`

## Therapist problems we solve
*(This sub-section is new and explicit because therapists are our future paying customers. Each problem maps to a feature they will later pay for.)*
- **Lead flow** — most therapists rely on word-of-mouth and have no digital acquisition channel. Platform fixes this.
- **Scheduling friction** — currently managed via WhatsApp messages back and forth. Platform replaces with a calendar.
- **No-shows and last-minute cancellations** — currently uncompensated. Platform tracks history per patient.
- **Payment tracking** — therapists lose track of who paid, when. Platform records (without holding) payment status.
- **Patient continuity** — no system for remembering basic facts about returning patients. Platform offers a simple patient list (Phase 1) and lightweight notes (Phase 2).
- **Online presence** — therapists with no website / no SEO. Platform profile becomes their public face.

## Market problems
- Fragmented mental health ecosystem `[validated]`
- No dominant digital platform `[validated]`
- Limited teletherapy infrastructure `[validated]`
- Lack of localized solutions `[validated]`

---

# 3. Market Opportunity

## Two markets, two sides
DzTherapy operates in two distinct markets simultaneously. Sizing both matters because we acquire one (users) to monetize the other (therapists).

### User side (acquisition target)
- **TAM:** ~15M Algerians aged 18–35 with a smartphone.
- **SAM:** ~3–4M urban (Algiers / Oran / Constantine / Annaba) with disposable income and at least occasional online purchasing behavior.
- **SOM (year 2):** ~10–30k who will try at least one online wellness session in our first 24 months. Rough guess; biggest unknown.

### Therapist side (paying customer)
- **TAM:** ~2,500 registered psychologists in Algeria + ~unknown number of psychiatrists/counselors actively practicing.
- **SAM:** ~500–800 in major cities, smartphone-comfortable, under 50, in private practice.
- **SOM (year 2):** ~50–150 active therapists on the platform by month 24, of which ~30–50 convert to paid subscription at launch.

## Hard constraints (not just market size)
- **Mobile-only:** ≥85% of access will be from mobile. Desktop is an afterthought.
- **Bandwidth:** 3G is common. Pages must load and video must work on slow networks. PWA over native, lazy-load everything.
- **Cultural framing:** "Mental health platform" reads as clinical/stigmatized. We position as **emotional wellness** and **safe conversations** in user-facing copy. "Therapy" is used in therapist-facing copy and in legal/regulatory contexts only.

## Positioning
The platform is positioned as:
- Emotional wellness platform
- Mental wellness support
- Safe conversations
- Stress and life management

**Not** positioned as:
- "Online therapy"
- "Mental illness treatment"
- "Replacement for clinical care"

---

# 4. Goals

> Goals are stage-gated and reflect the free-then-subscription model. We do **not** track session revenue as a Phase 1 KPI because we don't earn it. Therapist engagement is the leading indicator of year-2 conversion.

## Months 0–6 (anchor cohort)
- 10 anchor therapists onboarded and live
- ≥50 sessions facilitated
- Therapists rate the tools ≥4/5
- ≥60% of sessions completed (no-show rate <40%)
- Founders have spoken to every active therapist at least 3 times

## Months 6–12 (growth)
- 30 active therapists
- ~30 sessions facilitated per month (steady-state)
- ≥50% of therapists active weekly
- User booking-completion rate ≥40% (started a booking → attended a session)

## Months 12–18 (validation of paid intent)
- 50+ active therapists
- Direct interviews with ≥30 active therapists asking "would you pay X DZD/month for this in 6 months?"
- Target: ≥40% say yes at 5,000 DZD/month tier

## Months 18–24 (monetization launch)
- Paid tier launches
- Target: ≥30% of active therapists convert within 90 days
- First MRR

## Long-term (3–5 years)
- 200+ paid therapists
- Expansion to Tunisia, Morocco
- Regional leadership in MENA digital mental health infrastructure

---

# 5. Target Users

## Primary user (acquisition target — narrow on purpose)
**Urban professional women, 25–35, in Algiers/Oran/Constantine.**
- French-speaking (Arabic comfortable but French is the primary content language)
- Smartphone-native, on Instagram and TikTok
- In a job or postgraduate program
- Dealing with anxiety, burnout, relationship friction, or post-graduation life transition
- Has at some point Googled "psychologue Alger" or asked a friend for a recommendation
- Currently spending 0 DZD on emotional wellness because the friction is too high

We will *also* serve men and other age cohorts; we just don't design for them in v1.

## Therapist user (future paying customer)
**Practicing psychologists and psychiatrists in private practice, ≤45 years old.**
- Already comfortable with smartphone + WhatsApp
- Has an established patient base but wants more
- Currently manages bookings ad-hoc via phone calls and WhatsApp
- Frustrated with admin (scheduling, no-shows, payment tracking)
- Has heard of teletherapy but not actively using a platform

## Deferred to Phase 3+
- B2B (companies, universities, clinics) — not in MVP.
- Coaches (non-clinical) — Phase 4+.
- Patients seeking psychiatric care — Phase 3+ (regulatory complexity).

---

# 6. Product Scope

## Phase 1 — MVP (months 0–4)

The MVP is intentionally minimal. The user-facing surface is just enough to be a credible funnel; the therapist-facing surface is where we over-invest, because that is what we will eventually monetize.

### User-facing (5 features)
1. **Email signup** — email + password only. No phone auth, no social login.
2. **Curated therapist list** — hand-picked, no search, no filters. Profile pages show photo, bio, languages, specialties, price.
3. **Book a session** — Calendly-style; therapist sets weekly availability, user picks a slot.
4. **Pay therapist directly (off-platform)** — booking flow shows the therapist's payment instructions (CCP/RIB/Edahabia handle). User clicks "I have paid" + optional receipt upload.
5. **Receive Daily.co video link** — auto-generated and emailed once payment is confirmed by the therapist.

### Therapist-facing (6 features — this is where the future revenue comes from)
1. **Therapist signup + verification** — manual review by founders. Identity, credentials, registration with Ordre des Psychologues (where applicable).
2. **Profile editor** — bio, credentials, specialties, languages, photo, payment instructions (CCP/RIB/Edahabia), session price.
3. **Weekly availability calendar** — set recurring availability, block specific times.
4. **Booking inbox** — incoming requests, accept/decline, view payment status, see upcoming sessions.
5. **Patient list** — name, contact, total session count, last session date. **This is the foothold for year-2 monetization** — every session adds value here, making the platform stickier over time.
6. **Daily.co video link** — auto-generated and shared with both parties on confirmed booking.

### Admin (founders only — internal tool, not a feature)
- Therapist verification queue
- Manual payment dispute resolution (rare, expected handful per month)
- Basic dashboard: bookings/week, active therapists, session completion rate

---

# 7. Features NOT Included in MVP

## Explicitly deferred to Phase 2 (months 4–12)
- In-app messaging between user and therapist
- Voice notes
- Search and filters (by gender, language, specialty, price)
- Anonymous display name option for users
- Session notes / lightweight EMR for therapists
- Wallet / recharge system
- Abuse reporting UI (handled manually via email in v1)

## Deferred to Phase 3+
- AI intake assistant
- AI mood tracking
- Mobile native apps (PWA only at MVP and Phase 2)
- B2B offerings
- Group therapy
- Advanced analytics dashboards

## Permanently out of scope
- AI replacing therapists
- Selling physical wellness products
- Insurance integration (no Algerian mental health insurance market to integrate with)
- Per-session commission (locked out by business model — see §16)

---

# 8. Localization Requirements

## MVP (months 0–4)
- **French only.** Matches the urban professional persona. Reduces translation/QA burden in a season where every hour matters.

## Phase 2 (months 4–12)
- **Arabic** added once user value is proven. RTL UI considerations from the start (CSS, component design).

## Phase 3+
- English added.
- Algerian dialect (Darja) considered for marketing/content only, not UI.

## Cultural adaptation (in MVP)
- Same-gender therapist preference signal in profile
- Text-first communication in tone
- Voice-note support deferred to Phase 2
- Low-bandwidth optimization from day 1
- Mobile-first, no desktop-only features

## Cultural sensitivity (in MVP)
- Avoid Western "self-care" branding aesthetic
- Trust-oriented language (verified, hand-picked, private)
- Discreet visual design — no stock photos of crying faces or yoga poses

---

# 9. Payments — Pass-Through Model

> This is the key strategic clarification of v2. The platform **does not process or hold money in MVP, by design.**

## Core decision
DzTherapy is a **discovery + scheduling + video link** platform. It is not a payment service provider. Users pay therapists directly using the therapist's own payment method.

## How it works in v1
1. Therapist lists their preferred payment method on their profile (CCP/RIB for bank transfer, Edahabia handle, "ask me on first message," or any combination).
2. After booking, user sees a screen with the therapist's payment instructions.
3. User pays out-of-platform (bank transfer, Edahabia, cash on first session — therapist's choice).
4. User clicks "I have paid" + optionally uploads a receipt.
5. Therapist confirms payment received in their inbox.
6. Daily.co link is sent to both parties.

## Why this is the right v1 choice
**Avoided:**
- SATIM merchant onboarding (typically requires a registered Algerian SARL/SPA + bank intermediary, weeks-to-months of paperwork, capital requirements).
- Edahabia / Algérie Poste merchant relationship.
- Payment service provider (PSP) licensing obligations.
- KYC / AML requirements that come with holding funds.
- Fraud liability for the platform.
- Chargeback / refund infrastructure.
- Tax handling on transit money.

**Trade-off accepted:** v1 has worse user-side UX than a Stripe-style checkout. With a curated, low-volume launch and a culturally familiar payment flow (bank transfer is normal in Algeria), this is acceptable.

## Year-2 plan (separate problem, smaller scope)
When monetization begins, we only need to charge **therapists** for their monthly subscription. That is one merchant relationship and a recurring debit — much smaller scope than user-side payment processing. At that point we evaluate:
- SATIM (CIB) for Algerian-issued cards
- Chargily, Guiddini, or other current Algerian aggregators (verify current status before counting on these)
- International rails (Stripe via offshore entity, requires legal restructuring)
- Bank transfer with manual reconciliation as fallback (acceptable at low subscriber count)

## Open question (flagged for the founder)
*Are we comfortable being a "discovery + scheduling + video link" platform that never touches money?* The founding team's answer is currently yes — confirm and lock in.

---

# 10. Privacy, Security & Trust

## Core principle
Trust is the most important aspect of the platform. Privacy posture is a competitive moat in a market where users distrust digital health products.

## Security requirements
- HTTPS everywhere; HSTS preload-listed
- Strong password policy + rate-limited login
- Encrypted database storage for personally identifying information
- **Note on "end-to-end" claims:** video sessions go through Daily.co, which terminates encryption server-side. Communication is *transport-encrypted*, not strict end-to-end. Marketing copy should not claim E2EE for video. (Strict E2EE would require self-hosting the SFU, which is out of scope.)
- Secure session management
- Reference framework: **Algerian Law 18-07** on personal data protection (2018), plus GDPR-inspired patterns where they exceed local law.

## Compliance surface is dramatically smaller because of §9
Because we do not hold payment data and do not process funds, we avoid PCI-DSS scope and most financial-data regulatory burden. This is a meaningful operational benefit of the pass-through model.

## Trust features
- Verified therapist badges (manual founder review)
- Transparent therapist profiles (credentials, registration number)
- Reviews and ratings — deferred to Phase 2 (gameable at low volume; risky for therapist morale early)
- Strong privacy messaging in copy

---

# 11. Legal & Compliance — Concrete Open Questions

> v1 of this PRD listed "areas to research." This is not enough. Below are concrete questions that must have answers from a qualified Algerian lawyer or regulator **before launch**.

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | Can a licensed psychologist in Algeria legally conduct a paid session via video call? | Founder + lawyer | Open |
| 2 | Is registration with the Ordre des Psychologues required for a therapist to be listed on a paid platform? | Founder + lawyer | Open |
| 3 | What is the platform's liability if a user self-harms after a session arranged via DzTherapy? | Founder + lawyer | Open |
| 4 | Do we need to be a registered SARL/SPA before going live, or can the founders launch as physical persons (auto-entrepreneurs) initially? | Founder + lawyer | Open |
| 5 | What disclaimers and Terms of Service do we need to limit liability and clarify that DzTherapy is a directory/booking tool, not a healthcare provider? | Founder + lawyer | Open |
| 6 | Does the pass-through payment model (§9) trigger any payment-services regulation in Algeria? | Founder + lawyer | Open |
| 7 | What is the legal status of cross-border data storage for Algerian patient data (e.g. Postgres on AWS Frankfurt)? | Founder + lawyer | Open |

These are blockers. Launch is not safe until #1, #3, #5, and #6 have written answers.

## Initial compliance posture
- Verify therapist credentials manually on intake
- Display platform disclaimers prominently in T&Cs and at booking time
- Define emergency escalation procedures (what does the platform do if a user signals suicidal ideation in any communication channel?)
- Lock in T&Cs and Privacy Policy reviewed by an Algerian lawyer

---

# 12. AI Strategy

## Phase 1 — none
**No AI features in MVP.** Reasons:
- AI matching is premature when the therapist count is in the dozens; manual matching is faster, more trustworthy, and *itself a marketing differentiator* ("hand-picked by our team").
- Mood tracking and intake assistant add scope and complexity without meaningfully changing the conversion of the free user funnel.
- Bootstrapped runway should not be spent on premium AI APIs before the core marketplace works.

## Phase 2 (months 6–12, optional)
- AI intake assistant — light triage to recommend 2–3 therapists based on user input.
- Daily mood check-in for users (CBT-inspired self-tracking).

## Phase 3+ (post-monetization)
- **Therapist Copilot** — session summaries, structured notes, follow-up suggestions. **This is potentially a paid-tier upsell** for therapists, increasing willingness-to-pay.
- Wellness assistant (reflective prompts, CBT exercises) for users.

## Permanent constraint
The platform must **never** market AI as a replacement for therapists. AI is positioned as supportive, educational, organizational, and reflective — never therapeutic.

---

# 13. Recommended Technology Stack

> Optimized for **bootstrapped runway**, not just buildability. Every choice prefers a free tier we will not outgrow in 18 months.

## Backend
- **Python + FastAPI** (or Next.js API routes if the team is JS-only — re-evaluate based on team skill, decide once)
- **PostgreSQL** — Supabase or Neon free tier
- **No Redis at MVP** — defer until we have a workload that needs it
- **No WebSockets at MVP** — no real-time messaging in v1

## Frontend
- **Next.js + TailwindCSS** on **Vercel free tier**
- Responsive PWA only — no React Native at MVP

## Mobile
- PWA in MVP and Phase 2
- React Native evaluated only after paid tier launches and we have revenue

## Infrastructure
- **Drop Kubernetes** — premature complexity, monthly cost
- **Drop Docker for local dev** unless team needs it; deploy directly to Vercel/Railway/Fly
- Object storage: free tier of Supabase Storage or Cloudflare R2 (cheaper egress)
- Transactional email: Resend or Postmark

## Video infrastructure
- **Daily.co free tier** — sufficient at launch volume
- Test on Algerian mobile networks **before** committing (this is in §22 as an open assumption)
- LiveKit considered if Daily.co cost grows past free tier

## Tools and observability (free tiers preferred)
- Sentry free tier for error tracking
- Plausible / Umami / PostHog free tier for analytics
- No paid CI/CD beyond GitHub Actions free minutes

---

# 14. System Architecture (High Level)

> The v1 PRD listed 9 microservices. That was wildly over-engineered for the MVP. The architecture below is a single-monolith design with three external dependencies. It will scale to 10× our 18-month projected load on the cheapest tier.

## MVP architecture
- **Single application** (Next.js + API routes, or Next.js frontend + FastAPI backend — pick one based on team skill)
- **One PostgreSQL database**
- **One transactional email provider** (Resend / Postmark)
- **Daily.co** for video rooms (created on booking confirmation)
- **No queue, no cache, no microservices**

## Modules within the monolith
- Authentication
- Users
- Therapists (profile, availability)
- Bookings
- Notifications (email-based)
- Admin (founder tools)

## Future architecture decisions (deferred)
- Add a queue when we add background jobs (Phase 2: SMS reminders, calendar sync).
- Add Redis when we add real-time messaging (Phase 2).
- Split into services only when monolith scaling actually hurts (probably never within 24 months).

---

# 15. Go-To-Market Strategy

> Sequenced around the **two-sided funnel**. Therapist supply must precede user demand — an empty marketplace is worse than no marketplace.

## Step 1 — Therapist acquisition (months 0–3)
**Founder-led outreach to 30 hand-picked psychologists in Algiers and Oran.**
- Channels: personal network, LinkedIn, direct visits to clinics.
- Pitch: *"Free tools, free leads from our marketing, no commission ever. We'll only ever charge a monthly fee for the tools — and only after you've had a year of value first. Your feedback shapes the product."*
- Goal: 10 anchor therapists committed by end of month 3.
- This is **founder work**, not marketing-team work.

## Step 2 — User acquisition (months 3–6)
**Content marketing in French**, starting once ≥10 therapists are bookable.
- TikTok + Instagram + Facebook
- Topics: anxiety, burnout, relationship stress, post-graduation life, parenting
- Founder or partner therapists become the on-camera face — trust comes from real people, not stock content
- Goal: drive bookings to seeded therapists

## Step 3 — Therapist scaling (months 6–18)
- Word-of-mouth from anchor cohort
- Light paid ads on Facebook/Instagram targeting psychologists professional groups
- Goal: 50 active therapists by month 18

## Step 4 — Monetization launch (months 18–24)
- Direct outreach to active therapists with paid tier offer
- Highlight retained value (their patient list, their booking history) as switching cost
- Goal: ≥30% conversion of active cohort

## What we do NOT spend on
- Paid user acquisition before therapist supply is solid
- Brand campaigns or PR before product-market fit
- Conferences, swag, events — until revenue exists

---

# 16. Business Model

## Revenue streams

### Years 1–2 (free phase)
- **Zero revenue.** This is intentional.
- Costs are minimized: free hosting tiers, Daily.co free tier, founder time, no salaries.

### Year 2+ (monetization phase)
- **Therapist monthly subscription.** The single revenue stream.
- **Pricing band to validate (not final):** 3,000–10,000 DZD/month.
- **Likely tier structure:**
  - Free tier with hard limits (e.g. ≤5 active patients, ≤10 sessions/month, no advanced features) — keeps small/casual therapists on the platform.
  - Standard paid tier (~5,000 DZD/mo) — full tools.
  - Pro tier (~10,000 DZD/mo, optional) — premium features (Copilot AI, advanced analytics, priority profile placement).

### Permanently off the table
- **Per-session commission, ever.** Locking this in now prevents it from being reintroduced under runway pressure later. The product story to therapists is "we never take a cut of your sessions" — breaking that promise would destroy trust and the business with it.

### Future optional revenue (year 3+, not committed)
- B2B wellness packages
- University partnerships
- API/integrations for clinics
- Premium AI features for therapists

## Cost structure (years 1–2)
- Hosting: ~0 DZD/mo (free tiers)
- Daily.co: ~0 DZD/mo at launch volume
- Email: ~0 DZD/mo on free tier
- Domain + minor tooling: ~5,000 DZD/mo
- Founder time: opportunity cost only
- Legal review: one-time ~50,000–200,000 DZD before launch

---

# 17. Key Metrics (KPIs)

> Stage-gated. Different metrics matter at different phases.

## Months 0–6
| Metric | Target |
|---|---|
| Active therapists | 10 |
| Sessions facilitated | ≥50 cumulative |
| Therapist NPS | ≥40 |
| Session completion rate | ≥60% |
| Founder-therapist conversations | ≥3 per active therapist |

## Months 6–18
| Metric | Target |
|---|---|
| Active therapists | 50 |
| Bookings per active therapist per month | ≥3 |
| Therapist retention (month-on-month) | ≥80% |
| User booking completion rate | ≥40% |
| Therapist "would pay X DZD/mo" interview yes-rate | ≥40% |

## Months 18–24
| Metric | Target |
|---|---|
| Paid therapists | ≥15 |
| Paid conversion rate (of active cohort) | ≥30% |
| MRR | ≥75,000 DZD by month 24 |
| Paid churn (monthly) | ≤5% |

## Not tracked at MVP
- **CAC / LTV** — meaningless when we don't charge.
- **Per-session GMV** — money flows therapist-direct, off-platform.
- **Conversion to paid sessions** — every facilitated session is a "paid session" (the therapist gets paid); this isn't a KPI for us.

---

# 18. Risks & Challenges (Re-Prioritized)

> v1 of this PRD listed risks without prioritization or mitigation. v2 reorders them and demotes payments significantly.

## #1 — Runway exhaustion before paid conversion *(EXISTENTIAL)*
- **Why:** Bootstrapped, 1–2 years of zero revenue is a long runway to maintain on personal funds.
- **Mitigation:** Keep burn near-zero (no salaries, free hosting tiers, no paid tools). Re-evaluate at month 9 — if we cannot reach paid conversion in 24 months, raise pre-seed or change model.

## #2 — Therapists don't convert when paid tier launches *(EXISTENTIAL)*
- **Why:** The entire model fails if therapists who got 18 months of free value walk away when the bill arrives.
- **Mitigation:** Validate willingness-to-pay continuously from month 6 onward (not at month 18 when it's too late). Build features that *create switching cost* — patient list, booking history, online reputation. Prepare a "grandfather pricing" carrot for early therapists.

## #3 — Therapist supply (chicken-and-egg)
- **Why:** No therapists = no users = no therapists.
- **Mitigation:** Founder-led recruiting; treat first 10 therapists as design partners with monthly check-ins; over-deliver on responsiveness in first 6 months.

## #4 — Legal and regulatory
- **Why:** Telemedicine licensure unclear; platform liability for adverse outcomes (self-harm, malpractice) unclear.
- **Mitigation:** Get the §11 questions answered before launch. Lawyer-reviewed T&Cs. Emergency escalation protocol.

## #5 — Cultural adoption
- **Why:** Algerians may not book online therapy at meaningful volume regardless of how good the product is.
- **Mitigation:** "Wellness, not therapy" positioning; hand-picked therapists; same-gender filter; anonymous-friendly UX in Phase 2.

## #6 — Daily.co reliability on Algerian mobile networks
- **Why:** Untested. If video doesn't work, the product doesn't work.
- **Mitigation:** Test before committing — see §22.

## Demoted (no longer existential)
- **Payments** — the pass-through model in §9 removes this from the critical path.

---

# 19. Success Factors

The most important success factors, in order:

1. **Therapist quality** — we win or lose on the trust users place in our roster.
2. **Founder-led therapist relationships** — there is no shortcut for the first 30.
3. **Runway discipline** — every avoidable cost shortens the path to dying.
4. **Privacy and trust posture** — the moat against future competitors.
5. **Localization (FR first, AR second)** — language is brand.
6. **Distribution (content + word-of-mouth)** — paid acquisition is not affordable.
7. **Therapist tooling stickiness** — what makes year-2 conversion possible.
8. **Technology execution** — important, but lower-stakes than the social/business work above.

---

# 20. Development Roadmap

## Phase 1 — MVP (months 0–4)
**Build:**
- Authentication (email)
- Curated therapist marketplace (no search/filter)
- Booking system (Calendly-style availability)
- Therapist profile + availability + booking inbox
- Patient list (therapist side)
- Daily.co video link generation
- Pass-through payment flow ("pay therapist directly" + "I paid" / "confirmed received")
- Founder admin tools

**Goal:** 10 anchor therapists, ≥50 sessions facilitated.

## Phase 2 — Engagement (months 4–12)
**Build:**
- In-app messaging
- Voice notes
- Search and filters
- Anonymous display name option
- Lightweight session notes (EMR-lite for therapists — strengthens monetization hook)
- Arabic localization
- Reviews / ratings (cautiously)
- Optional: AI intake assistant

**Goal:** 50 active therapists; therapist retention ≥80%.

## Phase 3 — Monetization (months 12–18)
**Build:**
- Therapist subscription billing (one merchant relationship; evaluate SATIM/Chargily/Guiddini/Stripe-via-offshore)
- Tiered features (free tier limits, paid tier perks)
- Therapist Copilot (AI session summaries) as paid-tier hook
- Mobile app evaluation (build only if PWA limits us)

**Goal:** ≥30% paid conversion of active therapists; first MRR.

## Phase 4 — Scale & Expansion (months 18+)
**Build:**
- B2B wellness packages
- University partnerships
- Regional expansion (Tunisia, Morocco)
- Advanced AI features

**Goal:** Recurring revenue growth; regional foothold.

---

# 21. Final Strategic Notes

## Core thesis (one sentence)
*The user marketplace exists to make the therapist SaaS sellable in year 2.*

Every product decision should pass that filter. If a feature helps users but doesn't make therapists more likely to subscribe in year 2, it is a luxury we may not be able to afford. If a feature makes therapists love the platform and depend on it, it is core, even if users never see it.

## What this startup actually is
- A trust platform (the cultural and reputational layer)
- A healthcare distribution channel (the user-acquisition mechanism)
- A therapist productivity tool (the future revenue product)
- A cultural transformation play (the long-term mission)

## Competitive advantages we are betting on
- Localized UX (no Western platform will customize for Algeria)
- Trust posture (no commission, no payment-touching, transparent verification)
- Therapist-first design (most platforms treat therapists as supply commodities)
- Founder-led therapist relationships (the moat that can't be cloned)
- Patient brand-building over years (compounds while competitors pay for ads)

## Final recommendation
Solve in this order: **trust → access → simplicity → monetization → scale → AI.**

The biggest challenges are not technological. They are:
1. Earning the trust of psychologists who have never been on a digital platform.
2. Earning the trust of users who have never paid for therapy.
3. Surviving 18 months of zero revenue without compromising either.

Technology is the easy part.

---

# 22. Validated vs Unvalidated Assumptions (Appendix)

> This appendix is the doc that should drive validation work *before* writing code. Every assumption below is currently load-bearing for the business. Status legend: **validated** (we have evidence), **assumed** (we believe but haven't checked), **must research** (regulatory/technical fact-finding required), **must test** (technical reality-check needed).

| # | Assumption | Status | If wrong, what breaks |
|---|---|---|---|
| 1 | Algerians 25–35 will book a hand-picked therapist on a free platform | **assumed** | The user funnel is empty; therapists get no leads; nothing else matters |
| 2 | Therapists will accept "user pays you directly, off-platform" friction in v1 | **assumed** | Therapists refuse to onboard or churn after a few bookings |
| 3 | Therapists will pay 3,000–10,000 DZD/month in year 2 for the tools and lead flow they have been getting for free | **assumed (HIGHEST LEVERAGE — biggest single risk)** | The entire business model fails; pivot or shut down |
| 4 | We can recruit 10 anchor therapists in 60 days via founder outreach | **assumed** | Launch slips by months; runway impact |
| 5 | Daily.co works reliably on Algerian mobile networks (3G/4G across major cities) | **must test** | Sessions fail; therapists and users blame the platform; trust gone |
| 6 | Bootstrapped founders can sustain ~18 months of zero revenue | **founder-known, not externally validated** | Have to raise prematurely or close |
| 7 | Algerian law allows licensed psychologists to conduct paid sessions via video without additional licensing | **must research** | Cannot legally launch; need a workaround or different model |
| 8 | A platform that does not process or hold money has no PSP licensing requirement in Algeria | **must research** | If wrong, our entire compliance approach is wrong; need to redesign or get licensed |
| 9 | Manual therapist verification (founder review of credentials) is sufficient for v1 trust | **assumed** | A bad-actor therapist incident destroys reputation and possibly the company |
| 10 | French-only UI is acceptable for the MVP user base | **assumed** | Lower conversion; possibly need to crash-add Arabic earlier than Phase 2 |
| 11 | The pass-through payment model produces acceptable user-side conversion | **assumed** | Bookings fall through at the payment step; need to consider in-platform payments earlier |
| 12 | Hand-picked, no-search-no-filter is sufficient for the first 6 months of users | **assumed** | If user volume grows faster than expected, search becomes urgent |

## Validation actions (sequence before coding)

1. **Interview 10 psychologists** (this week / next): Would you list yourself for free with no commission? Would you pay 5,000 DZD/mo for tools + leads in 18 months? Will you accept "user pays you directly" friction?
2. **Get answers to legal questions §11.1, §11.3, §11.5, §11.6** from an Algerian lawyer (this month).
3. **Test Daily.co** from an Algerian mobile network (3G and 4G, two major cities) before committing the stack.
4. **Interview 10 potential users** (urban professional persona): Would you book a hand-picked therapist? Are you comfortable paying via bank transfer / Edahabia? What price feels right?
5. **Lock in the founder runway commitment** in writing (months of personal funds available before paid conversion is required).

If assumptions 1, 3, 7, or 8 turn out to be false, the model needs to change before code is written. Better to discover this in conversations than after 6 months of building.
