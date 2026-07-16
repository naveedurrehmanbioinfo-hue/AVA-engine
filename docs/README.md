# AVA Console Engine — Documentation

Official source documents for the **grounded knowledge-assistant platform** (working name), with **AVA for AIAG** as client #1 / anchor deployment. Built by 99xlab. Target: October 2026 cutover replacing the rented Betty AI foundation.

## Read order

1. **[eng-handoff-readme.md](./eng-handoff-readme.md)** — Aaron's handoff note. Read first: packet contents, expectations, the "no budget numbers yet" rule, ground rules.
2. **[99xlab-engineering-brief.md](./99xlab-engineering-brief.md)** — The brief. Client situation, market bar, architecture, the two novel subsystems (agentic KG pipeline + closed feedback loop), the ownership question, the 8 discovery spikes (§10), phases, definition of done.
3. **[ava-vs-cam-evidence.md](./ava-vs-cam-evidence.md)** — AIAG's own 44-question scored test of the incumbent + CAM side-by-side. The failure taxonomy the platform exists to fix; the first 47 golden-set seed cases.
4. **[grounded-chatbot-platform-build-plan.md](./grounded-chatbot-platform-build-plan.md)** — The generic platform build plan that sits on top of the AIAG engagement: product definition, architecture (SAI + Model Gateway + grounding system), pricing/tiers, legal, build phases.
5. **[ava-console-mockup-eng.html](./ava-console-mockup-eng.html)** — The admin console, interactive. **Product spec, not a sketch.** Seven screens: Dashboard · Knowledge · Instances · Conversations · Insights · Evals & Release · Settings & Audit.

## The one sentence

The LLM writes the *wording* of an answer; it never supplies the *facts*. Every factual field (title, duration, price, dates, entitlement, prerequisites) comes from typed, authoritative records — validated before display, refused or omitted when unverifiable. The surrounding system (source authority, effectivity, entitlements, evals, feedback loop) is the product; the model is a component.

## The six zero-tolerance gates (product requirements, not aspirations)

Invented resource titles · broken answer links · wrong member entitlement · expired/superseded item presented as current · unsupported regulatory claim · cross-instance content leakage — **all zero, regardless of average pass rate.**
