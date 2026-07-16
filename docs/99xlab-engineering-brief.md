# 99xlab Engineering Brief — Knowledge Platform (working name) · First deployment: AVA for AIAG
**99xlab · Internal · June 2026 · Owner: Aaron**

## 0. Why you're reading this

We're going to build a knowledge-assistant platform, and the first deployment replaces a live commercial product at a real client with a hard deadline. This brief exists so the team can wrap their heads around the whole thing — the client situation, the market bar, the architecture, the two genuinely novel subsystems (an agentic knowledge-engineering pipeline and a closed feedback loop), the unresolved ownership question, and what we need from each of you in the next four weeks. Client-facing packaging is handled separately; the engineering happens here at 99xlab.

Read this end to end once. Then read §10 (Discovery & spikes) again, because that's where your names go.

## 0A. The value prop, the finding, and the sequencing rule

**The value prop (official, use these words):** *AVA is designed and evaluated for AIAG's member work.* Not "smarter than Betty," not "better than Copilot" — designed and evaluated for the client's actual member tasks, and proven on a blind set of their real questions. Everything below serves that sentence.

**The finding that frames the product.** On July 9 we ran three real AIAG questions through CAM chat. It nailed the hard part — from a loosely-phrased request it correctly resolved a person (Timo Unger), a regulation (ELVR), a prior conference, and the right webinar. Then it reported the runtime as **76:08**. The live AIAG catalog page says **124.03 minutes** (verified against aiag.org/training-and-resources/webinars/details/CIEA). The model found the right thing; **the system failed to verify one field.** That single discrepancy is why this platform is not "a better-prompted chatbot": the LLM should write the *response*, but it must never invent or stale-cache the *facts* — title, duration, price, dates, availability, entitlement, prerequisites come from typed, authoritative records (see §6A). The surrounding system — source authority, effectivity, field validation, evals — is the product. The model is a component.

**The sequencing rule (Aaron's directive — hold this line):** **Phase 1 replaces Betty. Phase 2 makes AVA know the user.** Concretely: at cutover, AVA must *Find* (locate the exact authoritative resource), *Explain* (why it's relevant), and *Choose from stated context* ("I'm new to IMDS" → recommend Basic Concepts before Advanced IMDS — context the user gives in the conversation, no integration required). *Choose from known context* (role, completed courses, corporate subscription contents) and *Act* (register, purchase, assign, build a team learning plan — transactions with confirmation) come **after** cutover, because they depend on AMS/commerce integration depth that must not put October at risk. *Improve* (the §8 feedback loop) ships in Phase 1 because it's how the system gets better from day one. Anyone who scopes member-profile personalization into the October build is scope-creeping the deadline.

## 1. The situation in five sentences

AIAG (Automotive Industry Action Group — the standards body behind APQP, PPAP, FMEA, CQI, MMOG/LE) runs a member-facing AI assistant called **AVA**, rented from **Betty AI**, a Blue Cypress company with 150+ association customers. AIAG pays an annual subscription; Betty's contract renews **August/September 2026**, and AIAG wants a decision before then with a possible cutover in **October**. We have proposed replacing the rented foundation with a platform AIAG owns, operated by us, at spend comparable to today's — the proposal, one-pager, reality-check doc, and an interactive console mockup already exist and have been through two rounds of correction against verified Betty facts. Our CAM's chat (our existing knowledge engine) **already outperforms Betty's AVA on answer quality** against AIAG-domain questions — that's our unfair advantage and the seed of the platform. The strategic goal is bigger than one client: build the platform once, deploy it as the best knowledge assistant in the market, with AIAG as the anchor customer and proof case.

## 2. What already exists (don't rebuild it)

- **The answering engine.** CAM chat outperforms AVA today. Discovery task #1 is an honest audit of how much of it is liftable into a standalone platform (retrieval, prompting, guardrails) versus entangled with CAM.
- **The brand OS** — design system, admin scaffolding, auth patterns. The console should be assembled from it, not invented.
- **The console mockup** (`ava-console-mockup.html`) — treat it as the **product spec**, not a sketch. Six screens are specified and interactive: Dashboard, Knowledge (sources CRUD, upload pipeline with visible stages, content browser, test bench), Instances, Conversations, Insights (outcomes, RAG-eval meters, themes, gap report, funnel, digests), **Evals & Release** (golden-set pass rate, release compare with gates, model A/B, SME review queue), Settings & Audit.
- **Client-facing documents** (proposal, briefs, positioning decks) exist and define what has been promised — and deliberately *not* promised — for October. They carry client branding and commercial framing, so they are excluded from this packet; every promise that binds engineering is restated in this brief (§0A, §4, §9, §11, §13).
- **A verified competitive fact base** — Betty's real pricing, real admin capabilities (including what they shipped in late 2025), and documented failures in AIAG's live deployment (broken-citation 404s, no self-knowledge, mixed-language replies, quote-stitching).

## 3. The market and the bar

Know the field, because "best knowledge assistant out there" is the stated goal and it has to mean something measurable.

**Vertical (association) incumbents.** *Betty AI* — the category leader; conversational, white-label, multi-instance, INSIGHTS analytics; shipped self-service content management, CSV bulk upload, sync mode, word clouds/return-rate/common-questions, early "ask your conversation data" analytics, and model-provider choice through late 2025. Assume every feature gap we identify today is on their roadmap. *Onyx Point AI* — Betty's most direct competitor; citation-forward, search-centric, association-only (e.g., American Foundry Society: 7,000 members, ~18,000 resources). *FuseNext* — federated search across AMS/LMS/CMS rather than conversational.

**Enterprise tier.** *Glean, Coveo* — permission-aware enterprise search/assistants; strong governance, expensive, not association-shaped. *Onyx (open-source, formerly Danswer)* — MIT-licensed self-hosted agentic RAG with connectors and permission-aware search; worth studying as an architecture reference and as proof that "self-hosted, owned" is a viable product category.

**Where we win.** Nobody in the vertical offers all of: client-owned deployment, a knowledge **graph/ontology** layer, an **eval-driven release console**, native CMS/SSO integration, identity-level business analytics fused with commerce, and an agentic content pipeline. The enterprise tier has pieces of the governance story but none of the association product shape. That intersection is the product.

**The bar, concretely.** "Best" = beats the incumbent **on the client's real question distribution, blind-graded** (that's the AIAG parity sprint), and holds these production numbers: faithfulness ≥ 0.95, context recall ≥ 0.90, citation validity ≥ 99.5% (every link resolves *and* the user is entitled to it), language correctness ≥ 99% with zero mixed-language replies, entitlement correctness 100% (no cross-instance leakage, ever), p95 latency ≤ 3.5s streamed, and a golden-set release gate at 95%. Anything less and "best" is marketing.

**One more thing worth reading:** Betty's own blog post "Why Building Your Association's AI Assistant Costs More Than You Think" — their build-vs-buy FUD, citing specific build budgets and effort figures (deliberately not repeated here — see the packet README's ground rules on estimate anchoring). It's aimed at association IT departments building from scratch with no AI expertise. That is not us: we have a working engine that already beats them, a product team, a design system, and an anchor client funding the build. But the article's warnings about edge cases, content freshness, and the long maintenance tail are *correct* — treat it as a free risk register written by the competitor.

## 3A. Positioning guardrails (what we claim, what we never claim)

- **Claim:** *AVA is designed and evaluated for AIAG's member work* — then prove it: "on a blind set of real AIAG questions and tasks, AVA produced more current, complete, source-valid, and actionable results than the current system." Performance first; **ownership supports the performance argument** (sources, rules, entitlements, evals, roadmap under AIAG control; value compounds instead of resetting at renewal) — it does not substitute for it.
- **Never claim "better than Copilot."** Too broad to prove, and it invites a feature contest with Microsoft. The honest, verified context (Russ, a VP of IT at a Microsoft shop, *will* ask): the UK government ran the largest public Copilot evaluations to date — DWP measured ~19 min/day saved, strongest on search/email/summarization, weaker on complex and nuanced material; the ~20,000-user cross-government experiment self-reported ~26 min/day with the same caveats; DBT found 72% satisfaction for drafting/summarizing but **no evidence the time savings translated into department-level productivity**, with quality issues on data-heavy tasks. Copilot is a *horizontal* drafting/summarization/retrieval layer over a user's own documents. AVA is *vertical*: canonical catalog, source precedence, effectivity rules, entitlements, prerequisites, standards relationships, refusal rules, evals, an accountable content owner. **Those are system properties, not model properties** — Copilot doesn't have them for AIAG and can't without someone building exactly this system. One line for the room: *generic copilots help people work with documents; AVA helps members navigate, apply, and act on AIAG knowledge.*
- **Never claim "Betty lacks feature X"** — see §3; features converge. The moat is the system + ownership + evals.

## 4. The product in one page

**Surfaces.** An embeddable chat widget (WCAG-AA, light/dark, streaming, citations, feedback, suggested questions) on the client's site; Microsoft Teams later; everything driven by the same API.

**Instances.** A deployment hosts N instances — for AIAG: **Basic, Unlimited, Audit, and an IATF legal instance**. An instance = a config record: knowledge scope (subscribed collections), persona + disclaimers (versioned), entitlement policy, theming tokens, API keys, analytics partition, retrieval policy. Isolation is enforced **at query time** by collection filters; high-stakes instances (IATF legal) get a physically separate index namespace and strictest decline-over-approximate behavior. Content lives once in **collections**; instances subscribe. Adding instance N+1 is config, not a project.

**Entitlements.** User tier (anonymous / non-member / member / subscriber / corporate seat / staff / admin) × instance → policy (quota, library depth, features). AIAG's live rules — 14-day unlimited trial → 1 question/day → paid annual individual subscription → corporate seats — are *policy data*, editable in the console, not code.

**The interaction model (with phase tags).** Find → Explain → Choose → Act → Improve:

| Mode | Member outcome | Phase |
|---|---|---|
| **Find** | Locate the exact authoritative resource | 1 (cutover) |
| **Explain** | Understand what it covers and why it's relevant | 1 (cutover) |
| **Choose** | A recommendation, not a list — best match with branches ("new to IMDS? start here") | 1 from *stated* context · 2 from *known* member context |
| **Act** | Watch/save links in-answer at cutover; register, purchase, assign, team learning plans (confirmed transactions) | light: 1 · transactional: 2 |
| **Improve** | Every interaction feeds gaps, staleness, demand signals back to AIAG | 1 (the §8 loop) |

**The Answer Contract.** Every member answer is generated as **structured output first**, rendered conversationally second, and validated before display. Required components: (1) direct answer; (2) best match / recommendation; (3) why it matches; (4) authoritative source; (5) currentness/effectivity; (6) access, prerequisites, price, availability where relevant; (7) the next useful action; (8) related material *only when it adds value, with the relationship explained* (a broader primer is not an equivalent substitute); (9) an explicit caveat when evidence is incomplete or conflicting. The contract is what turns "lists five courses" into "recommends Advanced IMDS if you already use IMDS, Basic Concepts if you don't, and the Global Chemical Regulation series if you meant organizational compliance" — recommendation logic is a first-class requirement, not a nice-to-have, because our July 9 test showed CAM's retrieval is ahead of its deciding.

**The console** (the mockup, productionized): Dashboard · Knowledge · Instances · Conversations · Insights · **Evals & Release** · Settings & Audit. The console is not an afterthought; it is half the product and the thing that makes the platform sellable beyond client #1.

## 5. The ownership question — the one decision we owe the business

Aaron's framing: "maybe we own the platform, or customize for them and they can own their instance — not sure how that would work." Here's how it would work. Three models:

**Model A — Bespoke build, full IP assignment.** We build it, client owns everything including platform code. Clean for the client, kills the platform business: every subsequent client is a re-build or a licensing headache. Only acceptable if we deliberately fork per client (expensive forever).

**Model B — Platform core + client-owned instance (recommended).** Two IP layers:
- **99xlab owns the platform core**: the codebase, pipelines, console, eval harness — the reusable product.
- **The client owns their instance, completely**: their cloud subscription and everything deployed into it, their content, indexes, embeddings, **their knowledge graph**, configs, personas, analytics data, conversation history, and brand assets. Plus a **perpetual, irrevocable license** to run the platform for their deployment, and **source escrow** (they get the code if 99xlab disappears or breaches SLA).
This is how the client's "own, don't rent" promise is kept *in substance* — they control their data, their destiny, their cost curve, and can walk away with a running system — while 99xlab keeps a product. It's the standard shape for serious single-tenant platform businesses.

**Model C — Multi-tenant SaaS.** Our cloud, per-tenant isolation, subscription pricing. Best margins, fastest onboarding for clients 2–10 — and it is literally Betty's model, which undercuts the sales pitch for ownership-motivated clients. Viable later as a second tier ("hosted" vs "sovereign" deployments), not for the anchor client.

⚠️ **Conflict to resolve before any SOW is signed:** the current AIAG proposal (Option B / "build-operate-own") says "platform IP assigned to AIAG." Under Model B that language must become "instance, data, graph, and deployment owned by AIAG; perpetual platform license + source escrow; 99xlab retains platform core IP." This is a business/legal decision, not an engineering one — but engineering must know the answer, because it dictates whether we build **tenant-clean from day one**. Recommendation: build tenant-clean regardless (strict separation of platform code from client config/data/branding; no client-specific logic in core; everything client-specific expressed as configuration, collections, policies, and theme tokens). It costs modest additional discipline now and buys us the entire platform business.

## 6. Architecture

Azure-first (client is a Microsoft shop; Teams is on the roadmap), portable by design, model-agnostic via a gateway. Everything below deploys into the *client's* subscription under IaC (Terraform/Bicep).

**Components.** Widget (embeddable JS/React) → API gateway (streaming chat; FastAPI/Python for AI paths, TypeScript acceptable for console BFF) → entitlement service (Entra ID SSO + ABAC policy: tier × instance × collection × feature, enforced at retrieval time, never just in the UI) → retrieval layer (**Azure AI Search**: hybrid BM25 + vector + semantic reranking — chosen specifically because this corpus is dense with exact identifiers like "CQI-9," "IATF 16949," "PPAP Level 3" where pure vector search fumbles) → **graph/ontology store** (spike: Neo4j vs Cosmos DB Gremlin vs Postgres graph tables) → answer generation behind a **model gateway** (LiteLLM-style; frontier model for answers, small model for routing/language/classification; prompt caching; ZDR/no-training terms) → validation layer → provenance log. Storage: Blob/ADLS for raw documents; Postgres/Azure SQL for metadata, collections, entitlements, citations, events, audit. Observability: Langfuse (self-hosted) or Azure-native tracing + OpenTelemetry. Evals: Ragas + custom graders, wired into CI/CD as release gates.

**The member answer path is deterministic, not agentic.** classify → normalize (expand acronyms, *preserve exact identifiers*, detect language, generate query variants, attach metadata filters) → hybrid retrieve (entitlement-filtered) → optional graph expansion (related standard, superseding edition, mapped training/product) → rerank (prefer current, authoritative, same-language; penalize superseded unless the question is historical) → assemble answer pack (chunks, citations, quote limits, per-instance disclaimers) → generate (grounded-only; decline with a useful next step if evidence is insufficient) → **validate** (claims supported? every factual field matches the §6A registry — mismatches omitted and queued? every citation URL resolves *and* is entitled? single language? instance boundary respected?) → log full provenance (user, instance, query, chunks, model, prompt version, citations, latency, cost, feedback). Agents are for the console and ops, where unpredictability is a feature, not the member path, where it's a liability.

## 6A. Source Authority & Effectivity Registry (+ Contradiction Queue)

This is the direct answer to the 76:08-vs-124.03 finding, and it ships **lean in Phase 1** for catalog resources (webinars, courses, manuals, events), expanding later.

**Canonical typed records.** Every catalog resource gets a structured record — `resource_id, canonical_title, resource_type, canonical_url, status, publication_date, effective_from/to, last_verified_at, duration, format, price_member, price_nonmember, entitlement, language, prerequisites, next_session_date, owner, source_system` — sourced from the governing system (for AIAG: the Sitefinity/catalog record, not a blog post, not a stale index). Factual fields in answers are **filled from the registry via tools, never generated**.

**Source precedence.** The system knows which source governs when two official sources disagree (catalog page > marketing page > archived PDF > crawl cache), which version is current, which differences are legitimate scope differences, and which conflicts need a human.

**Field-level validation.** The answer validator (§6 pipeline, "validate" step) checks every factual field against the registry. On mismatch it applies the **omit-until-reconciled policy** — better no runtime than a wrong runtime — and files a record in the **Contradiction Queue**: `resource, field, indexed value, catalog value, status, response policy, owner, detected date`. The queue lives in the console's Knowledge screen next to the ingestion approval queue; admins resolve, the registry updates, `last_verified_at` refreshes. Staleness monitoring re-verifies high-traffic records on a schedule.

This is deliberately operational, not theatrical: the product does not force all organizational knowledge to "balance" — it knows what governs, what's current, what's withheld, and who owns the exception.

## 7. The agentic knowledge-engineering pipeline (the new thing #1)

This is Aaron's "agent team adds knowledge to an ontology and/or graph, or builds a new graph" — and it's buildable now, not speculative. The 2024–2026 literature and tooling are directly on point: Microsoft **GraphRAG** and **LightRAG** established LLM-driven entity/relation extraction into queryable graphs; **KARMA** demonstrated the multi-agent, schema-guided pattern (specialist agents per stage with an ontology boundary); ontology-grounded two-step extraction and **AutoSchemaKG**-style schema induction cover the "extend the ontology when new concepts appear" case; KG²RAG and FalkorDB's GraphRAG SDK show the retrieval payoff (graph-aware retrieval materially reduces hallucination on cross-document questions). We're assembling proven parts into a product pipeline, with one non-negotiable addition: **a human approval gate**.

**On ingest (upload, crawl, or CMS sync), a supervised agent team runs:**
1. **Parser agent** — structure-aware extraction (Azure Document Intelligence + fallback), tables, images-to-descriptions, strikethrough-as-obsolete detection.
2. **Metadata agent** — language, edition, publication/review dates, suggested collections and entitlement level. Confidence-scored; low confidence routes to a human.
3. **Extraction agent** — entities and relations *against our ontology*: Document, Edition, Section, Requirement, Definition, Standard family, Training course, Store product; relations like `supersedes`, `implements`, `requires`, `applies_to`, `available_in_language`, `maps_to_training`.
4. **Ontology curator agent** — fits extractions into the existing ontology; where a new concept doesn't fit (say, Catena-X entities), *proposes* a schema extension with evidence. **Proposals never auto-apply.**
5. **Graph builder** — writes approved nodes/edges with per-assertion provenance (source doc, chunk, extractor version, confidence).
6. **Consistency/QA agent** — duplicate-entity resolution, contradiction detection (two docs disagree on a requirement), edition-conflict flags, orphan detection.
7. **Eval-seeding agent** — drafts candidate golden-set Q&A pairs from the new content so coverage grows with the corpus.

**Human-in-the-loop is the design, not a caveat:** the console's Knowledge screen gets an **approval queue** — proposed entities/edges/schema changes with evidence, one-click approve/reject/edit, full audit trail. Target state: agents do 95% of the graph-building labor; a curator (client-side or ours) spends minutes a day approving. That queue is also a demo moment no competitor has.

**The graph must earn its existence** — by improving retrieval, recommendation, entitlements, effectivity, or action; never to produce an impressive visualization. Note from the July 9 test: the first two questions (find a webinar, find a Scope 3 resource) needed only strong search and clean metadata — the graph pays off on the *third* kind (prerequisite paths, "which training for this role," supersession, cross-standard synthesis). Entities to add beyond documents/standards: **Person/Presenter, Role, Skill level, Regulation, Action**; relations: `presented_by, covers, requires, builds_on, recommended_for, answers_questions_from, scheduled_for, included_in_subscription`.

**Why the graph earns its complexity here:** AIAG's corpus is *made of* relationships — APQP ↔ Control Plan ↔ PPAP ↔ IATF 16949 clauses; FMEA 4th Ed superseded by AIAG-VDA; standards mapped to trainings and store products; every manual existing in six languages. Flat vector search answers "what is X"; the graph answers "how does X relate to Y," "what changed," "what should I take first," and powers related-resource recommendations that convert to revenue. Phase 1 ships a lightweight ontology + graph expansion in retrieval; Phase 2 deepens it. Do not let graph ambition slip the October date — the deterministic RAG path must be excellent *without* the graph, and better *with* it.

## 8. The feedback loop (the new thing #2 — "feedback that goes somewhere")

Every 👍/👎 + comment, every decline, every low-confidence answer, every citation click (and non-click) is an **event**, and every event has a destination:

- A **classifier agent** triages feedback: `wrong_answer` | `content_gap` | `stale_content` | `ux_issue` | `feature_request` | `praise`.
- `wrong_answer` → **SME review queue** (already in the mockup's Evals screen) + auto-drafted regression case for the golden set.
- `content_gap` / `stale_content` → the **gap report**, clustered nightly by topic, with an agent-drafted **content brief** the client's content team can pick up.
- `ux_issue` / `feature_request` → tagged into the product backlog with the conversation attached.
- Aggregates surface in Insights (feedback rate, resolution rate, time-to-resolution) and in the weekly digest — so the client *sees* feedback becoming fixes.
- **Close the loop visibly:** when a gap identified by member feedback gets new content or a corrected answer, the system can note it ("this answer was updated on …") and the digest credits it. Feedback that visibly changes the product is a retention feature, an eval-data flywheel, and something Betty's "thumbs up/down → CSV" does not do.

## 9. Quality system

**Start thin, this week — the 100-question starter set.** We already have 44 seeded: AIAG's own CR/SC test of AVA (see `ava-vs-cam-evidence.md`) — 44 real questions graded by AIAG staff themselves, roughly half thumbs-down, every failure mapped to a platform component. Those plus the July 9 CAM trio are entries #1–47; grow to the full 300–1,000 from Betty INSIGHTS exports. Category targets: catalog/resource lookup (15), training recommendations & prerequisites (15), currentness/versions/supersession (15), cross-standard & cross-resource synthesis (15), membership & entitlement correctness (10), actions & transaction handoffs (10), multilingual behavior (10), unknown/misleading/unsafe requests (10).

One **golden set** per deployment (for AIAG: 300–1,000 real questions harvested from Betty INSIGHTS exports, stratified by instance/topic/language/difficulty, seeded with every known failure). **Graders:** Ragas-style (faithfulness, context recall/precision, answer relevancy) + ours (intent resolution, authoritative-source selection, **factual-field accuracy against the registry**, currentness/effectivity, citation-URL validity, **recommendation quality** — did it decide, or just list?, entitlement correctness, edition correctness, action correctness, language correctness, refusal/appropriate-uncertainty correctness, policy-safe summarization, latency and cost). **Gates:** no release ships below 95% golden-set pass — and averages hide unacceptable errors, so six conditions are **absolute zeros regardless of the average**: invented resource titles = 0 · broken answer links = 0 · wrong member entitlement = 0 · expired/superseded item presented as current = 0 · unsupported regulatory claim = 0 · cross-instance content leakage = 0. Enforced in CI, visible in the console's Evals & Release screen (release compare, regression-by-release, model A/B, SME queue). The same harness produces the **Betty-baseline scorecard** that wins the AIAG decision in September. Targets are in §3; they're product requirements, not aspirations.

## 10. Discovery & spikes (weeks 1–3 — this is where your names go)

**Learn from the client:** per-instance volumes (INSIGHTS export — the single most time-sensitive item), Sitefinity version + API scope, SSO/IdP + AMS entitlement source of truth, corpus inventory (documents × languages × editions), Betty contract end/notice/export terms, whether "Basic" is a knowledge scope or an entitlement state, IATF legal instance requirements.

**Engineering spikes (timeboxed, one owner each, written findings):**
1. **CAM engine audit** — what's genuinely liftable; interfaces to extract; entanglement risks. *This gates the whole estimate.*
2. **Retrieval bake-off** — Azure AI Search hybrid+semantic vs pgvector+reranker on ~50 real AIAG questions incl. exact-identifier and ZH cases.
3. **Parser bake-off** — Document Intelligence vs Unstructured-class tools on 5 real manuals (one ZH, one with strikethrough, one table-heavy).
4. **Agentic KG extraction quality** — run the §7 pipeline on 5 manuals; measure entity/relation precision against a hand-built reference; estimate curator minutes per document.
5. **Graph store selection** — Neo4j vs Cosmos Gremlin vs Postgres graph tables for our query patterns (expansion during retrieval, supersedence chains, entitlement-scoped traversal).
6. **Entitlement engine** — OpenFGA / Oso / Cedar / Postgres-rules spike against the tier × instance × collection matrix; must prove query-time filter pushdown into retrieval.
7. **Widget skeleton** — streaming, citations, feedback events, theming tokens on brand OS; measure p95 to first token.
8. **Registry & field validation** — pull typed catalog records (duration, price, dates, prerequisites, entitlement) from Sitefinity for ~50 resources; wire the validator to check answer fields against them; reproduce and *catch* the CIEA runtime mismatch automatically. This spike proves the §6A concept end-to-end.

## 11. Phases (AIAG track; platform track runs parallel where marked)

- **P0 · Discovery & proof setup (now → early July):** everything in §10; golden set v1; SOW + **ownership model resolved (§5)**; cloud account stood up under IaC. *(Platform: tenant-clean repo structure, config schema.)*
- **P1 · Core build (July → mid-Aug):** ingestion + collections + instances; retrieval hardening; **canonical registry v1 + answer contract + field validation + contradiction queue**; widget; entitlements; console alpha (Knowledge, Conversations, Dashboard); analytics tier 1; provenance + audit log. *(Platform: everything config-driven.)*
- **P2 · Parallel run & eval (mid-Aug → mid-Sep):** full corpus in; agentic KG pipeline on the corpus with curator queue; blind Betty-vs-us eval; language QA; IATF isolation tests; load test; UAT. **Scorecard delivered before the client's renewal decision.**
- **P3 · Cutover & hypercare (Oct):** widget swap, daily monitoring, broken-citation alerting, feedback triage live, 30-day hypercare. Expect a bug tail; staff for it.
- **P4 · Exceed (Q4 →):** **first: member/org context — "AVA knows the user"** (role, entitlements, completed courses, corporate subscription contents via AMS/SSO — declared and authorized context, not silent profiling) → **then transactional actions** (register, purchase, assign, team learning plans, always show-and-confirm) → graph deepening, Teams app, in-conversation commerce, CQI-9 training pilot, China options analysis, tier-3 analytics. *(Platform: package for client #2.)*

## 12. Honest risks

The estimate leans on **CAM reuse** — if spike #1 comes back entangled, timeline and cost move; say so early. **Betty is shipping** — assume feature-parity arguments expire; our moat is ownership + graph + evals + integration depth (see the reality-check doc §1A before repeating any competitive claim). **Three years of their edge-case polish** — the eval harness and hypercare are the answer, not optimism. **Graph scope creep** — the October date is won by the deterministic RAG path; the graph makes it better, not possible. **Ownership language conflict** (§5) — unresolved, blocks the SOW. **China** is a Phase-4 options analysis, not a promise. And Betty's build-vs-buy article is right about the maintenance tail: we are signing up to operate this for years — the run-book, alerting, and support rotation are part of v1's definition of done, not afterthoughts.

## 13. Definition of done — v1 (AIAG cutover)

Four instances live in the client's cloud under IaC; entitlements enforced at query time with zero cross-instance leakage in testing; ingestion (crawl w/ canonical de-dup, Sitefinity sync, uploads, YouTube) visible and re-runnable in the console; agentic KG pipeline running with curator approval queue; console shipping Dashboard/Knowledge/Instances/Conversations/Insights/Evals/Settings; feedback loop routing to queue + gap report + golden set; answer contract enforced as structured output; registry + field validation + contradiction queue live for catalog resources; eval gates in CI with the published targets met, including the six absolute zeros; provenance on every answer; scorecard vs Betty delivered; run-book + on-call rotation staffed; 30-day hypercare complete.

## 14. Reading list

*Ours:* the console mockup — **engineering edition** (`ava-console-mockup-eng.html`, the product spec) · **ava-vs-cam-evidence.md** (AIAG's own 44-question scored test — the failure taxonomy every engineer should internalize) · the packet README. *(Client-facing materials carry client branding and commercial framing and are deliberately excluded; ask Aaron if a spike genuinely needs one.)* *External:* Microsoft GraphRAG (Edge et al., 2024) and LightRAG (Guo et al., 2024) · KARMA multi-agent KG construction (2025) · AutoSchemaKG (schema induction, 2025) · "LLM-empowered knowledge graph construction: a survey" (2025) · Ragas metrics docs · Langfuse docs · Azure AI Search hybrid + semantic ranking docs · Onyx (open-source) repo as an architecture reference · Betty's build-vs-buy article — **read only AFTER your bottom-up estimate is submitted**: it is the competitor's risk register and it contains cost/effort anchor figures in both directions and Betty's Oct 2025 product-updates post (know exactly what they ship before claiming they don't) · GOV.UK Copilot evaluations — DWP trial evaluation (Jan 2026), the cross-government M365 Copilot experiment findings, and the DBT pilot evaluation (Aug 2025) — the verified basis for the horizontal-vs-vertical positioning in §3A.

---
*Questions → Aaron. First team session: walk the mockup screen by screen, assign the §10 spikes, and pressure-test the §5 recommendation.*
