# Build Plan — "Grounded" Knowledge Chatbot Platform
*A Betty-class platform where organizations build their own knowledge assistant on their own storage and their own models — and where every answer is verifiably grounded or refused.*

---

## 0. Execution context — AIAG is client #1 and the 99xlab brief is the execution path

This plan does not replace the engineering brief; it sits on top of it. The AIAG deployment (P0–P4, October 2026 cutover, the 8 spikes) **is** Phases 0–1 of this platform, executed under a hard deadline for a paying anchor client. The rules that follow from that:

- **The brief's sequencing rule governs.** Nothing platform-generic is allowed to put October at risk. Platform work runs in parallel only where the brief already marks it: tenant-clean repo, config schema, everything-as-configuration. That discipline is the entire platform strategy — hold it and the generic product falls out of the AIAG build almost for free.
- **What AIAG pays for that the platform keeps:** Answer Contract, typed registry + contradiction queue, validation layer, refusal engine, eval harness + release gates, feedback loop, widget, console, instances + query-time entitlements. All of it is generic if built tenant-clean. The AIAG scorecard becomes the platform's founding proof asset.
- **What gets deferred to post-cutover (P4 / client #2 packaging):** additional storage adapters beyond whichever backend wins spike #2 (the loser of Azure AI Search vs pgvector becomes adapter #2 later — the SAI abstraction ships now, the second implementation doesn't), customer-facing BYO API keys (the model gateway ships for AIAG anyway, so BYO keys are a thin addition later), per-seat self-serve billing, the WordPress plugin, and self-serve onboarding.
- **Ownership must be settled as Model B before the SOW is signed.** The current proposal language ("platform IP assigned to AIAG") would kill this platform business at birth. It must become: AIAG owns their instance, data, indexes, graph, and deployment, with a perpetual license and source escrow; 99xlab retains the platform core. This is now the single most urgent commercial item on the plan.
- **Pricing:** AIAG is not on the per-seat SaaS model — they're a build-operate engagement at spend comparable to their current Betty subscription. The §3 tier structure applies from client #2 onward. AIAG's IATF legal instance doubles as the proof case for the Legal tier (isolated namespace, strictest refusal profile, audit trail) — build it once, sell it twice.

## 1. Product definition

**One sentence:** A self-serve platform where any organization connects its knowledge base, picks its own storage backend and LLM provider, and deploys a citation-first chatbot widget to any website — with a hard guarantee that the bot answers only from verified sources and refuses everything else.

**The USP, stated as a contract, not marketing:**

1. **Grounded-only generation.** The LLM writes the *wording* of answers; it never supplies the *facts*. Every factual claim must trace to a retrieved chunk or a typed record.
2. **Self-verification before display.** A validation pass checks every answer against its evidence before the user sees it. Claims without support are stripped or the answer is replaced with a refusal.
3. **Honest refusal.** If the knowledge base doesn't contain the answer, the bot says so — with a useful next step (suggest related content, offer to log the gap) — rather than improvising. Refusal correctness is a first-class quality metric, not a failure mode.
4. **Real citations.** Every answer carries resolvable links to the exact source passages. Broken or unentitled citations are a zero-tolerance defect.
5. **Bring your own infrastructure.** Storage/retrieval backend (Azure AI Search, AWS OpenSearch/Kendra, pgvector, Pinecone/Qdrant/Weaviate, Neo4j for graph) and model provider (OpenAI, Anthropic, Google, Azure OpenAI, Bedrock, or self-hosted) are pluggable, with customer-supplied API keys.

**Why this wins against Betty-class incumbents:** they are closed, single-stack, rented systems whose quality claims can't be inspected. This platform's pitch is *inspectable trust* — customers see the eval scores, the citation validity rate, and the refusal behavior, and they own their keys, their data, and their vector store. Features converge over time; the trust architecture and the BYO model don't.

---

## 2. Architecture

### 2.1 High-level shape

```
Widget (embeddable JS) 
   → API Gateway (streaming chat, REST + SSE)
      → Auth & Entitlement service (seats, tiers, per-collection permissions)
      → Query pipeline (deterministic, not agentic):
           classify → normalize → retrieve (via Storage Adapter)
           → optional graph expansion → rerank
           → generate (via Model Gateway, grounded-only prompt)
           → VALIDATE (claim support, citation resolution, entitlement, language)
           → stream to user + log full provenance
      → Ingestion pipeline (crawl / upload / CMS sync → parse → chunk → embed → index)
   Admin Console (tenant dashboard, knowledge mgmt, evals, analytics, billing)
```

The member-facing answer path is **deterministic** — a fixed pipeline, not a free-running agent. Agents belong in ingestion and ops (metadata extraction, gap classification), where unpredictability is tolerable. In the answer path it's a liability.

### 2.2 The two abstraction layers that make BYO possible

**Storage Adapter Interface (SAI).** A single internal contract — `index(chunks, metadata)`, `hybrid_search(query, filters, k)`, `delete(namespace)`, `health()` — with one adapter per backend:

| Adapter | Notes |
|---|---|
| pgvector + reranker | Default managed option; cheapest; ship first |
| Azure AI Search | Hybrid BM25+vector+semantic rerank; best for identifier-heavy corpora |
| AWS OpenSearch / Bedrock KB | For AWS-native customers |
| Qdrant / Weaviate / Pinecone | Popular vector-native choices |
| Neo4j / Postgres graph tables | Graph expansion layer (Phase 3), sits *beside* the vector adapter |

Hybrid search (keyword + vector) should be the required baseline in every adapter — pure vector search fumbles exact identifiers (SKUs, standard codes, part numbers), which are exactly what knowledge-base corpora are full of.

**Model Gateway.** A LiteLLM-style routing layer: per-tenant provider config, customer-supplied API keys stored encrypted (KMS/Key Vault, never logged), model switching per instance, automatic fallback, prompt caching, cost metering per tenant/seat, and enforcement of zero-data-retention / no-training API terms where the provider offers them. Use a frontier model for answer generation and a small cheap model for classification, language detection, and routing.

### 2.3 The grounding system (the actual product)

This is where the USP lives; everything else is commodity.

1. **Answer Contract.** Answers are generated as *structured output first* (direct answer, evidence references, why-it-matches, source list, confidence, caveats), rendered conversationally second, and validated before display.
2. **Typed fact registry.** For structured facts — prices, dates, durations, versions, availability — the model never generates the value; it calls a tool that reads a canonical typed record synced from the customer's system of record (CMS, catalog, database). Field-level mismatch between index and registry → the field is **omitted, not guessed**, and a contradiction record is queued for an admin.
3. **Validation layer (post-generation, pre-display):**
   - *Claim support check:* an NLI/grader pass verifies each claim is entailed by retrieved evidence; unsupported claims are removed or the answer downgraded to refusal.
   - *Citation validator:* every URL must resolve (HTTP check, cached) AND be topically attached AND be entitled to the asking user.
   - *Language check:* answer language matches query language; zero mixed-language replies.
   - *Scope check:* no content from collections the tenant/instance/seat isn't subscribed to.
4. **Refusal policy engine.** Per-tenant configurable strictness (a "legal" instance declines on any ambiguity; a marketing instance can be looser), but the floor is universal: no evidence → no answer, plus a logged content gap.
5. **Eval harness as a release gate.** Each tenant gets a golden question set (seeded from their real queries). Graders: faithfulness, context recall, citation validity, refusal correctness, entitlement correctness, latency, cost. No platform release ships below a pass-rate gate, and some defects are absolute zeros regardless of averages: invented titles, broken links, wrong entitlements, stale-presented-as-current, cross-tenant leakage.

This eval layer is also a *sellable feature*: tenants see their bot's scorecard in the console. No incumbent exposes that.

### 2.4 Ingestion

Sources: website crawl (with canonical de-dup), file upload (PDF/DOCX/PPTX/HTML/MD), CMS sync (WordPress REST API, Sitefinity, Contentful, Notion), sitemap, YouTube transcripts. Pipeline: parse (structure-aware — tables, headings, strikethrough-as-obsolete) → chunk → extract metadata (language, dates, type; low-confidence routes to human review) → embed → index via the tenant's adapter. Every stage visible in the console with re-run buttons and an approval queue for anything an agent inferred.

### 2.5 The widget

Vanilla-JS embeddable bundle (<50 KB gzipped core), one `<script>` tag plus a data attribute for the instance key. Works on WordPress (also ship a thin WP plugin wrapper for the marketplace), Shopify, Webflow, and any custom site. Streaming responses, inline citations with hover previews, 👍/👎 + comment, suggested questions, theming tokens (colors, radius, font, position), WCAG-AA, light/dark, mobile-safe. All traffic through the public API so Teams/Slack/native apps can follow later on the same contract.

### 2.6 Multi-tenancy and isolation

- Tenant → N instances (e.g., "Public site bot," "Members bot," "Legal bot"), each a config record: knowledge scope, persona + disclaimers (versioned), refusal strictness, entitlement policy, theme, API keys, analytics partition.
- Isolation enforced **at query time** via mandatory collection filters pushed into the storage adapter — never just hidden in the UI. High-stakes instances (legal) get a physically separate index namespace.
- Cross-tenant leakage is a zero-tolerance defect tested on every release.

---

## 3. Pricing, seats, and tiers

Per-seat subscription with instance/usage dimensions layered on. A "seat" = a named admin/staff user of the console and analytics; end-user chat traffic is metered separately (messages/month) so the widget can serve anonymous visitors.

| | **Starter** | **Pro** | **Enterprise** | **Legal / Regulated** |
|---|---|---|---|---|
| Price shape | Low flat + per-seat | Per-seat + usage | Custom annual | Custom annual, premium |
| Seats | 2 included | 5 included, +per seat | Volume-priced | Volume-priced |
| Instances | 1 | 3 | Unlimited | Unlimited, isolated namespaces |
| Storage backend | Managed pgvector only | + BYO vector DB | + Azure/AWS BYO, graph | Dedicated/sovereign deployment option |
| Models | Platform keys, metered | BYO API keys | BYO + fallback routing | BYO with ZDR-verified providers only |
| Grounding | Standard validation | + typed registry, contradiction queue | + custom graders, release gates | Strictest refusal profile, human-review queue mandatory |
| Compliance | Standard ToS | DPA on request | DPA, SSO/SAML, audit log export, SLA | + full provenance retention, eDiscovery export, source escrow option |
| Support | Community | Email | CSM + SLA | CSM + named legal-ops contact |

Design notes on the model:

- **Per-seat alone under-monetizes** a widget product (a tenant with 3 admins might serve a million visitors). Seats price the console; **message volume prices the widget**; BYO keys mean inference cost passes through to the customer, which keeps your margins clean and is itself a selling point ("your OpenAI bill, your negotiated rates, no markup").
- The **Legal tier** is the halo product: strictest refusal, mandatory human review before certain answer categories go live, immutable audit trails, longer provenance retention, and contractual language about the assistant being an *information retrieval aid, not advice*. Price it 3–5× Pro; regulated buyers pay for defensibility.
- Annual billing default for Enterprise/Legal; monthly for Starter/Pro to reduce friction.

---

## 4. Legal standpoint

*(I'm not a lawyer — treat this as an issues list to take to one, ideally with UK coverage given JSK Logics' registration, before onboarding the first paying tenant.)*

**Liability and disclaimers.** The core exposure of any answering system is a user acting on a wrong answer. Mitigations: (a) ToS limiting liability and disclaiming reliance, with the assistant positioned as an information tool; (b) per-instance disclaimer text that tenants control and that renders in the widget; (c) for the Legal tier specifically, contractual language that output is not legal/professional advice, plus the mandatory human-review workflow as an operational (not just verbal) safeguard. Your grounding architecture is itself a liability defense — provenance logs let you show exactly what source produced a claim.

**Data protection.** You'll be a **processor** for tenant knowledge bases and end-user chat logs; tenants are controllers. You need: a standard DPA with sub-processor list (cloud, model providers), UK GDPR / EU GDPR compliance (SCCs or UK IDTA for transfers), data-residency options for Enterprise/Legal (deploy into the tenant's region or their own cloud subscription), retention controls, and a deletion pipeline that actually purges embeddings and indexes, not just the source docs. Chat transcripts can contain personal data end-users type in — say so in the DPA and give tenants redaction/retention knobs.

**Model provider terms.** BYO keys shift a lot of this to the tenant's own provider agreement — document that clearly. Where you supply platform keys (Starter), you carry the provider terms; use ZDR/no-training endpoints and state it. For the Legal tier, restrict the model list to providers with contractual no-training and enterprise data terms.

**IP in three directions.** (1) *Tenant content:* tenants warrant they have rights to what they ingest; you take only a license to process it. (2) *Output:* assign output rights to the tenant. (3) *Platform:* you retain platform IP; tenants get a subscription license — and for Enterprise/Legal you can offer **source escrow** (they get the code if you fold or breach SLA), which is a powerful closer for ownership-motivated buyers without giving away the platform. For AIAG specifically this is the live issue: the existing proposal's "platform IP assigned to AIAG" language must be renegotiated to the Model B shape (instance + data + graph + deployment owned by AIAG; perpetual license + escrow; platform core retained) *before* the SOW is signed — every future client's economics depend on that clause.

**AI-specific regulation.** EU AI Act: a knowledge chatbot is likely limited-risk → transparency duty (users must know they're talking to an AI — build the "AI assistant" label into the widget, non-removable). UK is lighter-touch today but watch it. If you sell into legal/medical/financial verticals, do a per-vertical risk classification rather than assuming limited-risk.

**Commercial hygiene.** Acceptable-use policy (no ingesting content the tenant doesn't own; no prohibited use cases), SLA definitions for Enterprise/Legal (uptime, support response, hypercare), clear export rights (tenants can take their data, indexes, and graph out — this is your anti-Betty pitch, so make it contractual), and insurance (professional indemnity / tech E&O) before the Legal tier launches.

---

## 5. Build phases

**Phase 0 — Foundations (weeks 1–3).** Tenant-clean monorepo; config schema (tenant → instance → collection → policy); auth (Clerk/Auth0 or Entra); Postgres for metadata/entitlements/events; Model Gateway v0 (2 providers + BYO keys, encrypted); Storage Adapter Interface with the pgvector adapter; CI with the eval harness skeleton. **Spike in parallel:** claim-support validation approach (NLI model vs LLM-grader vs structured-output-only) on 50 real Q&A pairs — this gates the USP, so it's your spike #1 equivalent.

**Phase 1 — Grounded core (weeks 3–8).** Ingestion v1 (upload + crawl + WordPress sync); deterministic query pipeline; Answer Contract as structured output; validation layer v1 (claim support, citation resolution, language); refusal policy engine; widget v1 (streaming, citations, feedback, theming); console alpha (knowledge management, conversations, dashboard); provenance logging on every answer. **Exit criterion:** a demo tenant where you can show a question it answers with citations, a question it *refuses* with a logged gap, and the provenance trail for both.

**Phase 2 — Multi-tenant SaaS (weeks 8–14).** Seats, tiers, billing (Stripe, per-seat + metered messages); second and third storage adapters (Azure AI Search, one vector-native); typed fact registry + contradiction queue; per-tenant golden sets and the tenant-visible eval scorecard; DPA/ToS/AUP finalized with counsel; WordPress plugin published. **Exit:** 3–5 design partners live on paid pilots.

**Phase 3 — Enterprise & Legal tier (weeks 14–22).** SSO/SAML; audit log export; isolated namespaces; the Legal refusal profile + mandatory human-review queue; graph adapter (Neo4j or Postgres graph) with retrieval-time expansion for relationship questions; deploy-into-customer-cloud option (Terraform); source-escrow paperwork; SLA + on-call rotation. **Exit:** first Enterprise/Legal contract signed.

**Phase 4 — Compound (ongoing).** Feedback loop productized (👎 → classified → gap report → drafted content brief); agentic knowledge-graph ingestion with curator approval; Teams/Slack surfaces; marketplace listings; usage-based analytics tier.

---

## 6. Team and cost drivers

Minimum viable team for Phases 0–2: one full-stack lead (pipeline + API), one frontend (widget + console), one AI/retrieval engineer (adapters, validation, evals), and fractional DevOps and design — a shape your existing bench can likely cover. The three biggest cost drivers to watch: (1) **inference** — mitigated by BYO keys, small-model routing, and prompt caching; (2) **the validation pass** — every answer costs a second model call; budget it per-message and reflect it in the metered price; (3) **the maintenance tail** — connectors, edge cases, and content freshness are a permanent operating load, so bake run-books, alerting, and support rotation into the definition of done for v1, not after.

## 7. Risks, honestly

- **"Zero hallucination" is a claim you must be able to survive.** Market it as *grounded-or-refused with published eval scores*, not as an absolute — one counterexample kills an absolute claim. The zero-tolerance gates apply to the defects you can make structural (invented titles, broken links, leakage).
- **Over-refusal is the mirror failure.** A bot that declines too often gets ripped out. Refusal correctness must be graded in both directions.
- **Incumbents ship.** Betty-class vendors will add citations and analytics; your durable moat is BYO infrastructure + inspectable evals + export rights, so make those contractual and loud.
- **BYO backends multiply your test matrix.** Each adapter is a permanent support commitment; add them behind demand, not speculatively.
- **The legal tier's promises must be operational.** Human review queues and audit trails have to exist and be staffed before a regulated customer relies on them.

## 8. First 30 days, concretely

1. Validate the claim-support spike (the USP gate).
2. Stand up the tenant-clean repo, config schema, gateway, and pgvector adapter.
3. Build the thinnest end-to-end slice: upload docs → ask → grounded answer with citations → refusal on an out-of-corpus question → provenance log.
4. Line up 3 design partners (associations, professional bodies, or agencies with knowledge-heavy clients) with a paid-pilot letter of intent.
5. Book a session with a UK solicitor on ToS/DPA/liability framing and the IP-separation question.
