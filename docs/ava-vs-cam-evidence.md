# Exhibit A — AVA (Betty Bot) on AIAG's Own Test, Side-by-Side with CAM
**99xlab · Internal · July 2026 · Source: AIAG CR & SC question test (CR-SC_Questions.docx) + CAM chat transcript, July 9**

## 1. What this document is

AIAG's own team (Corporate Responsibility and Supply Chain areas) ran **44 real questions** through AVA and graded the answers themselves — thumbs up/down with comments. Separately, we ran the first three CR questions through CAM chat. This document tallies AIAG's own scoring, puts the overlapping questions side by side, extracts the failure taxonomy, and converts all 44 questions into golden-set seed cases. It is the single most persuasive evidence asset in the project, because the grades are *the client's*, not ours.

## 2. The headline, honestly stated

On AIAG's own test, **AVA cleanly satisfied roughly half the questions** (~23 of 44 clearly positive; ~21 thumbs-down, incorrect, or partial — a few gradings in the source notes are ambiguous, and one "failure" is arguably correct behavior; see §5). The failures are not random: they cluster into seven repeatable patterns, every one of which maps to a specific platform component we've already specified. That's the story: **AVA's failures are structural, not incidental — and structure is exactly what a rented chatbot can't give AIAG.**

Handle the number with care: this was a single-rater, expert-authored test skewed toward hard cases. Don't quote "~50%" externally; re-score blind under the eval rubric during the parity sprint and let that number be the official one.

## 3. The direct side-by-side (same questions, both systems)

**Q1 — "Point me to the webinar from Timo Unger regarding the latest updates on ELV and answers to questions from last year's IMDS conference"**
- **AVA:** a bare URL. AIAG's grade: **👎 "failed to get me the information."**
- **CAM:** correctly resolved person (Timo Unger, Hyundai Europe), regulation (ELVR), the prior IMDS 2025 conference, and the right webinar (CIEA) — with title, link, description, format, category. AIAG's implicit grade of the same task: this is what they wanted.
- **CAM's own miss, on the record:** it reported the run time as **76.08 minutes**; the live AIAG catalog page says **124.03**. Right resource, one stale/wrong field. This is the §6A Source Registry case study — and it stays in every internal telling, because it's why the registry and field-validation exist.

**Q2 — "Point me to the webinar on Scope 3?"**
- **AVA:** the title only. AIAG's grade: **👎 "failed to get me the information,"** plus the damning margin note: **"AVA not aware of old or new webinars"** — a catalog-coverage failure, not a language-model failure.
- **CAM:** correct webinar (SCOPE), presenter, description, format, complimentary access, run time (~63 — matches the page's 63:29), *and* a genuinely related broader resource (Carbon Inventory Management Workshop) with the relationship explained. Per the Answer Contract, the related item should be visually distinguished as broader-not-equivalent — minor polish, right instinct.

**Q3 — "What training provides me with compliance readiness, such as Chemistry Manager?"**
- **AVA:** "Advanced IMDS." AIAG's grade: **👎 "pointed me to wrong training."**
- **CAM:** listed three legitimate paths (Advanced IMDS; IMDS V11.0 Update & Chemistry Manager; the 3-part Global Chemical Regulation series) with descriptions.
- **The lesson cuts both ways.** Note the nuance: the AIAG catalog *does* list Advanced IMDS as covering Chemistry Manager — yet the tester called it wrong, because the question was ambiguous between *tool operation* and *organizational compliance readiness*, and a single unbranched pick failed the person asking. AVA decided without branching and lost; CAM listed without deciding and merely survived. The Answer Contract's target behavior is the third option: **recommend with branches** — "If you already use IMDS → Advanced IMDS (covers Chemistry Manager, next session Sep 28). New to IMDS → start with Basic Concepts. If you meant organizational compliance → the Global Chemical Regulation series." Also: any version-specific course (V11.0) must be confirmed current via the registry before being recommended.

## 4. The failure taxonomy — every pattern maps to a component we've specced

| # | Pattern (AIAG's own words) | Examples from their test | The component that fixes it |
|---|---|---|---|
| 1 | **Bare links instead of answers** ("failed to get me the information") | Timo Unger Q, Scope 3 Q, tariff/Section 232 webinar Q | **Answer Contract** — direct answer + why it matches + metadata + next action, enforced as structured output |
| 2 | **Catalog blindness** ("AVA not aware of old or new webinars") | Webinar discovery; CR Assessments materials Q ("not familiar with webinars"); ESGR/ESGD missed | **Ingestion coverage + Source Registry** — typed records for every catalog resource; coverage monitored, gaps alarmed |
| 3 | **"List all X in area Y" fails** → generic landing page | "All eLearnings in Corporate Responsibility" and "…in Supply Chain" both → generic /elearning | **Typed catalog queries** — registry filter (`type=eLearning AND area=CR`) answered as a real list, not a link |
| 4 | **Broken or irrelevant citations** | Labeling Standards Q cited **a 404 document unrelated to the topic** (second documented 404, after the June screenshots) | **Citation validator** — links must resolve *and* be topically attached; broken-citation rate is a monitored zero |
| 5 | **Wrong entity/group mapping** | IMDS-enhancement group ≠ Supplier Alliance; FVL question missed the EV Battery Transportation & Handling work group; "H&S workgroups" answer not grounded in the CR side | **Ontology/graph relations** — groups, topics, and resources as typed entities with `works_on`, `related_to` edges |
| 6 | **No procedural guidance** | Newsletter answer omitted "scroll down and click submit"; certificate-included question unanswered | **Answer Contract fields** — access/prerequisites/availability are required components filled from the registry |
| 7 | **Feedback goes nowhere** | Tester's margin note on the FVL miss: "**Talk to marketing**" — a human manually routing a content fix | **The §8 feedback loop** — 👎 → classified → gap report → auto-drafted content brief → visible resolution |

Recommendation-quality failures (Q3 above; "assessment results reporting" → should have been MMOG training; SCM assessments including FVLKA wrongly) sit across patterns 1 and 5 and are why *"did it decide, or just list?"* is a first-class grader.

## 5. Where AVA did fine — say so, it strengthens the case

AVA answered the **CTPAT/customs-and-trade cluster** well (eight consecutive thumbs-ups): deep questions against a single authoritative page it had clearly ingested. It also handled event registration, DDRT applicability, conflict-minerals onboarding, MMOG/LE scheduling, and ISO 14001 lookup. And one "failure" deserves defending: asked for "the most common security gaps found in risk assessments," AVA declined — *"I don't have a reliable, source-backed list… based on the material available to me."* **That refusal is correct behavior** when the corpus lacks the answer; our system must preserve honest declines (refusal correctness is a grader) while the decline itself routes to the gap report. The pattern is clear: AVA is serviceable when one well-crawled page holds the answer, and fails when the answer requires the *catalog*, a *relationship*, a *recommendation*, or a *procedure*. Those are system properties. That's the pitch.

## 6. What these 44 questions become

They are golden-set seed cases, mapped to the starter-100 categories: catalog/resource lookup (the webinar and template questions), training recommendations & prerequisites (Chemistry Manager, assessment-reporting), currentness/effectivity (V11.0 course, run times), cross-resource synthesis (CR Assessments materials), entitlement/procedural (certificate-included, newsletter), actions (event registration, purchase paths), and refusal correctness (security-gaps decline). Every thumbs-down becomes a regression case with AIAG's own comment as the grading note; every thumbs-up becomes a don't-break case. The scorecard narrative for September writes itself: *"On your own test, the current system cleanly passed about half. Here is the same test, blind, on both systems."*

## 7. Cautions before this leaves the building

The sample was authored by AIAG subject-matter staff — expert phrasing, skewed hard, single rater; a few grades in the source notes are ambiguous (two tariff/security entries read as merged). Use it internally as the definitive failure taxonomy and seed set; use it externally only after the blind re-score under the published rubric. And keep CAM's 76.08 runtime miss in every internal version — the credibility of this whole evidence chain rests on grading ourselves as hard as we grade Betty.
