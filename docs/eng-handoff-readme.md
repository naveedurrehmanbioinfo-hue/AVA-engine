# READ ME FIRST — Engineering Handoff Packet · Knowledge Platform / AVA
**99xlab · Internal · July 2026 · From: Aaron**

## What's in this packet, in read order

1. **`99xlab-engineering-brief.md`** — the brief. Read end to end, then read §10 (spikes) twice.
2. **`ava-vs-cam-evidence.md`** — AIAG's own 44-question scored test of the incumbent (AVA/Betty) plus our CAM side-by-side. This is the failure taxonomy the platform exists to fix, and the first 47 golden-set cases.
3. **`ava-console-mockup-eng.html`** — the admin console, interactive. **This is the product spec, not an inspiration board.** Click everything: instance switcher, upload pipeline, test bench, Evals & Release. All analytics values are sample data.

## Why there are no budget numbers in this packet — read this

You will notice this packet contains **no fee figures, no budget targets, no vendor price points, and no third-party effort estimates**. That is deliberate. Your week-3 deliverable includes an **independent, bottom-up quote** — effort by workstream, staffing, duration, assumptions, contingencies, and price — built from the spikes, and I don't want any number in your head before your own. The only commercial constraints you need are qualitative and real: the client currently rents this capability under an annual subscription; the replacement must be **cost-comparable to what they pay today**; and run costs (cloud + inference) must be a small fraction of that. Client-facing documents with commercial framing exist and are excluded; if a spike genuinely needs one, ask me. Related ground rule: the competitor has published a build-vs-buy article containing cost and effort anchors in both directions — it's listed in the brief's reading list as **read-after-you-quote**, and I mean it.

## What I expect back

**Within 48 hours (read-back):** each engineer has read items 1–3; a 30-minute session where the team walks *me* through the architecture and the §5 ownership models in their own words, and challenges anything that looks wrong. If nobody pushes back on anything, I'll assume it wasn't read.

**End of week 1:** spike owners assigned (all 8, one name each); spike #1 (CAM engine audit) **started first** — it gates every estimate; a written list of what you need from the client/discovery that isn't already in §10; and any "this can't be true" flags on the October timeline, raised now rather than in September.

**End of week 3 (spikes complete):**
- A one-pager per spike — findings, recommendation, confidence, what it changes. Specifically: the CAM reuse verdict (the big one); retrieval bake-off on the 50-question sample; parser verdict on 5 real manuals incl. ZH; agentic-KG extraction precision + curator-minutes-per-document; graph store pick; entitlement engine pick with proof of query-time filter pushdown; widget p95-to-first-token; and spike #8 catching the CIEA runtime mismatch automatically.
- **The quote:** an independent, bottom-up estimate mapped to P0–P4 — effort by workstream, staffing shape, duration, assumptions, risk contingency, and price. Show your math; ranges with confidence beat false precision.
- A tenant-clean repo skeleton with the config schema drafted.

**What good looks like:** disagreement with specifics ("Azure AI Search loses to pgvector+reranker on our ZH cases, here's the data"), scope pushback with alternatives ("the contradiction-queue UI slips to P2; the validator + omit-until-reconciled policy ships P1"), and estimates with stated confidence. **Red flags:** "it's just RAG, easy" (means §6A/entitlements/evals weren't understood); polishing UI before spike #1 reports; anyone scoping member-profile personalization into October (§0A sequencing rule); quoting the ~50% incumbent failure rate externally before the blind re-score; anyone hunting for budget numbers instead of estimating from the work.

## Ground rules

- The value prop is fixed language: *AVA is designed and evaluated for AIAG's member work.* Performance proven blind; ownership makes it compound.
- The six zero-tolerance gates are product requirements, not aspirations: invented titles, broken links, wrong entitlements, expired-as-current, unsupported regulatory claims, cross-instance leakage — all zero.
- The LLM writes responses; it never invents facts. Title, duration, price, dates, availability, entitlement, prerequisites come from typed records (§6A). The 76:08-vs-124:03 miss is our own — grade ourselves as hard as we grade the incumbent.
- Anything client-facing routes through Aaron.

Questions → Aaron. First session: mockup walkthrough, spike assignment, pressure-test ownership Model B.
