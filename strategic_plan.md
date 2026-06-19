# TermsIQ — Strategic Deployment and Commercialisation Plan
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 3.0 — June 2026

> **How to read this document.** Each section below has two parts: a **🟢 Client-Facing** block — the language and figures appropriate to share with a prospective client — followed by a **🔒 Internal Only** block with the vendor's underlying business case (build costs, founder pay, vendor ROI, margin thresholds). The internal blocks are not for client distribution; they exist so the same document serves both as the client deliverable and as the underlying business plan, without two files drifting out of sync. 

---

## 1. Deployment Phases

### 🟢 Client-Facing

**Phase 1 — Proven Capability (complete)**
TermsIQ has already been validated across five real supplier/country combinations — extracting all five critical T&C fields (third-party liability cover, pickup grace period, licence rules, payment rules, cross-border conditions) with 100% field resolution and zero fields requiring human review. This is the working capability the rest of this plan builds on; it is not a concept, it is a measured result on real supplier documents.

**Phase 2 — Pilot (Months 1–6)**
Your top 50 supplier/country combinations are mapped, configured, and run in shadow mode — TermsIQ's output is compared against your existing manual process for a minimum of four weeks, with nothing yet served to your OTA partners. Three structured workshops run during this phase:

- **Week 2 — Co-design:** defining the validation workflow and exception-handling rules together with your content team
- **Week 6 — Accuracy review:** reviewing real extraction-vs-source comparisons on your own documents
- **Week 10 — Impact review:** assessing readiness for go-live

Nothing goes live until your team has seen and approved the results against the Greenlight Criteria in Section 5.

**Phase 3 — Full Deployment (Month 7 onward)**
The validated 50 combinations go live, and coverage expands toward your full supplier/country footprint — up to 250 combinations under the Growth tier (or further under Enterprise terms if your footprint is larger). From this point:

- T&C data is served live to your OTA partners via API
- Daily monitoring catches supplier document changes automatically, with updates reflected within 24 hours
- A case study is produced from your results, with your agreement on what's shared externally

**Phase 4 — Expansion (Year 2+, optional)**
Coverage can grow beyond the original five fields and beyond your initial markets as your needs evolve — more supplier/country combinations, more T&C fields, more geographies, all under the same pricing structure described in Section 3.

---

### 🔒 Internal Only

**Phase 1** was built as a prototype — essentially zero hard cost, no contracted engineering team, no infrastructure spend. Its job was to prove the extraction approach works before committing real budget. **This is not the same thing as the "build" referenced in the ROI's upfront cost** — that figure covers what comes next: turning this proven prototype into the production-grade system.

**Phase 2** is the ROI's upfront-cost period — **€137,350 (midpoint) over six months**, covering the AI/NLP and backend engineering work to close the gaps catalogued in the MVP documentation (OCR for scanned documents, headless browser rendering for JS-only pages, a PostgreSQL knowledge base with version history, the human review interface, audit trail and compliance tooling), plus legal, GDPR, and EU AI Act review.

**Phase 3**: the system goes live, matching the ROI's go-live assumption (A13: "Allows 6 months build + validation before production"). The pilot client pays the **full Growth tier subscription rate from this point — no discount.** Ongoing cost from this point is **€91,055** (midpoint) for the first six live months, rising to **€180,710/year** (midpoint, including a real founder/consultant fee and a legal/compliance retainer) from Year 2.

**Phase 4 is not optional growth — it is required for the business to reach sustainable margin.** At 3 clients (the Phase 3 target), the business runs at an annual loss of roughly €30,710 once the founder's own pay is counted as a real cost. **5 clients is the realistic minimum scale** at which the business covers its full cost base and starts generating genuine margin (~€69,290/year at 5 clients).

---

## 2. Timeline and Milestones

### 🟢 Client-Facing

| Phase | Timing | Milestone |
|---|---|---|
| Phase 1 — Proven Capability | Complete | 5/5 supplier/country combinations validated; 25/25 fields resolved; demo-ready |
| Phase 2 — Pilot | Months 1–6 | Source mapping and API integration complete (Week 1–2); co-design workshop (Week 2); accuracy review workshop (Week 6); impact review workshop (Week 10); ≥4-week clean shadow mode completed |
| Phase 3 — Full Deployment | Month 7 onward | Validated 50 combinations live; coverage expansion toward full footprint begins; case study published once results are measurable |
| Phase 4 — Expansion | Year 2+ (optional) | Additional T&C fields and markets added as agreed |

The single hard gate in this timeline is the end of Phase 2: Full Deployment does not begin until the Greenlight Criteria in Section 5 are met.

---

### 🔒 Internal Only

| Phase | Timing | Cost (ROI midpoint) |
|---|---|---|
| Phase 1 — POC → MVP | Complete | ~€0 (prototype) |
| Phase 2 — Pilot | Months 1–6 | €137,350 upfront |
| Phase 3 — Full Deployment | Month 7 onward | €91,055 (months 7–12, incl. founder fee) |
| Phase 4 — Scale *(required for sustainability, not optional)* | Year 2+ | €180,710/year (incl. founder fee + legal retainer) |

**What the vendor ROI says about this timeline, stated plainly:**

The 12-month vendor ROI is **−81%** — expected, because the build cost is concentrated in Year 1 and only one client (the pilot) is generating revenue. Revenue grows at a realistic pace of **one new client signed per year** from Year 2 onward — not two simultaneously, which would be optimistic for a 2–4 month sales cycle with a small founding team. By the end of Year 3, this reaches 3 total paying clients: annual subscription revenue of €150,000 against ongoing costs of €180,710/year — **still a loss of roughly €30,710/year at 3 clients.** This is the central finding: 3 clients, even at a properly cost-based price, is not enough for the business to be sustainable. **5 clients is the realistic minimum** — at that scale, revenue (€250,000) clears the full cost base (€180,710) with genuine margin (~€69,290/year). At a 1-client-per-year pace, 5 clients isn't reached until roughly **Year 5** — meaning either the sales pace needs to accelerate, or the founder should plan for a longer runway than 3 years.

The Growth tier price of €50,000/year was deliberately built bottom-up from the vendor's actual fully-loaded cost base — including a real founder/consultant fee and a legal/compliance retainer — rather than being set low to make the client's ROI look more dramatic. The client's case remains strong at this price (see Section 3, internal pricing rationale), so there was no need to underprice the product.

This plan doesn't soften the investment picture. Year 1 is a cost year by design. The business case rests on reaching 5 paying clients by the end of Phase 4, not 3 — this is the single most important number for any investor or stakeholder conversation about this plan's viability.

---

## 3. Go-to-Market and Commercial Approach

### 🟢 Client-Facing

**Who this is for:** TermsIQ is built for car rental aggregator API providers — typically 50–300 employees, managing connectivity for 100–500 suppliers, who are currently absorbing OTA partner complaints about T&C accuracy and facing EU consumer-law regulatory pressure.

**How the relationship works:** This isn't a self-serve product — it's a direct, hands-on engagement, sized to a 2–4 month evaluation-to-decision window. The clearest way to evaluate it is the live demo: a real Hertz or Sixt T&C document, extracted in seconds, with full source attribution on every field — available before any commitment is made.

**Pricing model:**

| Tier | Coverage | Annual price |
|---|---|---|
| Pilot | 50 combinations, validated in shadow mode (Months 1–6) | Same rate as Growth tier from Month 7 — no markup, no hidden discount-then-increase |
| **Growth** | Up to 250 combinations | **€50,000/year** |
| Enterprise | 250+ combinations, multiple markets | €90,000+/year, custom terms |

Plus a one-time onboarding fee (€10,000–25,000, depending on scope) covering source mapping, API integration, and the three Phase 2 workshops. A self-hosting licence option is available if your data-residency requirements rule out shared infrastructure.

**Source mapping is a shared task:** you provide the list of your target supplier/country combinations and whatever you already know about each document's location; the technical verification — confirming each source is reachable, classifying its format, configuring extraction — is handled for you.

**Why TermsIQ vs. the alternatives:**

Against your current process — a content team manually reading supplier PDFs — TermsIQ is faster and catches changes between review cycles that a manual process would miss.

Against generic document-AI or OCR tools — the differentiator is domain depth: extraction logic tuned to how each rental company actually structures its T&C documents, built-in resolution of statutory-minimum liability figures against the official COB reference table, and full field-level provenance on every output.

Against building it yourself — this is already a working, measured pipeline, not a from-scratch engineering project for your team to take on.

Against doing nothing — the regulatory environment makes this a live risk, not a hypothetical one. The EU Consumer Centres Network logged 6,016 complaints about car rental companies in 2025, and 55% of screened online intermediaries were found to violate EU consumer law on T&C transparency. The European Commission has already taken formal enforcement action against five major suppliers (2017–2020) for exactly this kind of clarity failure.

On third-party liability specifically — this is the field most likely to matter directly to your customers, not just your compliance team. Most OTAs today can only tell a customer "statutory minimum applies," which means nothing to someone comparing two rental options at checkout. Being able to state the real figure (e.g. "€70,000,000 personal injury cover in Spain," not "as required by law") turns a compliance field into a concrete trust signal at the point of sale — one a competitor can't match without the same capability behind it.

---

### 🔒 Internal Only

**Target buyers:** The primary buyer is the CCO or Head of Supplier Partnerships at a car rental aggregator API provider. The technical evaluator is the CTO or VP Engineering. The day-to-day user is the Content or Product Manager who currently owns manual T&C maintenance — their adoption determines whether data quality actually improves after rollout, which is why they're engaged as a co-designer in Phase 2 rather than informed after the fact.

**Sales channel:** Direct, B2B, sales-led — not self-serve. Decision made at CCO/CTO level, typical sales cycle 2–4 months.

**Pricing rationale (cost-based derivation):** The ongoing cost base is €180,710/year (midpoint, Year 2–3, including a real founder/consultant fee and a legal/compliance retainer, alongside engineering, infrastructure, and monitoring costs). At 3 clients, splitting that cost three ways means each client needs to clear roughly **€60,237/year** just to cover its share of ongoing cost — before any margin, which is why 3 clients alone does not make this business sustainable. At **5 clients**, the realistic minimum scale, the per-client cost floor drops to roughly **€36,142/year**, leaving room for the €50,000/year tier price to generate real margin. These tier prices are sized against a real, fully-loaded cost floor that includes the founder's own pay, not just external contractor and infrastructure bills.

**Consulting/implementation fee:** The Phase 2 onboarding work specific to each client is billed as a one-time fee (€10,000–25,000) separate from the recurring subscription. This keeps the subscription price clean and predictable while still covering the real, client-specific setup cost — a smaller, per-client slice of the same kind of work the ROI's upfront change-management line items cover at the platform level.

**Licence model:** for clients with strict data-residency or self-hosting requirements — a larger upfront licence fee plus a smaller ongoing support/update fee, with hosting cost shifting to the client. Secondary option, not the default.

**Per-use cost — why it isn't a standalone pricing model:** Across the actual GPT-4o-mini extraction runs (five supplier/country combinations, nine total LLM calls), total token usage was 33,191 tokens for a complete initial extraction batch. At GPT-4o-mini's actual pricing ($0.15/million input tokens, $0.60/million output tokens), that's roughly **€0.006 for the entire five-combination batch**, or about **€0.0012 per supplier/country combination**. A 50-combination pilot batch costs roughly €0.06 in API calls; a 250-combination Growth-tier client's batch costs roughly €0.30. This confirms AI API cost is not the cost driver behind this product — a genuine per-use price would be too small to matter on its own. Per-use cost is evidence for why the subscription model is priced the way it is; it isn't a pricing model in its own right.

**TPL as differentiator, internal framing:** an inaccurate or fabricated TPL figure shown to a customer is the highest-stakes version of the R4 hallucination risk in the ROI document, since it's a number a customer might actually rely on when choosing where to book.

---

## 4. Stakeholder Communication

### 🟢 Client-Facing

Different people in your organisation need different things from this engagement. This is what each role should expect to hear, and when.

| Your stakeholder | What they need to hear from us | When |
|---|---|---|
| **Executive sponsor** (CCO or equivalent) | The business case: the regulatory and reputational risk of the status quo (6,016 EU complaints in 2025, active EC enforcement environment), what Phase 2 proves before any live data is served, and the go/no-go decision point at the end of the pilot. No commitment to Full Deployment is required until results are in hand. | Kickoff; end of Phase 2 (pilot results); Phase 3 go-live decision |
| **Head of Supplier Partnerships** | How their day-to-day role shifts from manually chasing supplier T&C updates to exception management and supplier engagement once the system is live; what's needed from them at onboarding | Phase 1 kickoff; Phase 2 scoping, ongoing |
| **Content / Product Manager** | They co-design the validation workflow in Week 2, see real accuracy comparisons in Week 6, and own the day-to-day human review queue from Phase 3 onward — approving or correcting any field flagged below the confidence threshold before it reaches customers. The system is built to support their judgement, not replace it. | Throughout Phase 2 via the three workshops; ongoing from Phase 3 |
| **IT / Engineering lead (CTO or VP Engineering)** | The integration is additive, not a replacement for existing systems — T&C data is appended to the current API response, cached rather than computed per request, with sub-50ms added latency. A defined fallback (`data_not_available`) is returned for any field below confidence threshold. | Technical spec review before Phase 2 integration begins |
| **Legal / Compliance lead** | TermsIQ's EU AI Act classification (Limited Risk, Article 50), confirmation that no personal customer data is processed as part of the core function, and the data processing agreement covering the relationship, including disclosure of any sub-processors used | Before Phase 2 integration begins; reviewed again before any OTA contract references TermsIQ data |
| **OTA / channel partners** *(informed later)* | Only once data-quality improvement is measurable — typically once the Phase 3 case study exists | Phase 3, once dispute-rate improvement and the case study are available |

---

### 🔒 Internal Only

| Stakeholder | What they need to know internally | Who communicates |
|---|---|---|
| **Chief Commercial Officer** (client-side, primary sponsor) | The vendor's own ROI is not shared with this stakeholder — see external framing above. Internally, the vendor's project lead tracks whether pilot results support the Phase 3 go/no-go and whether the sales pace can realistically exceed 1 client/year. | Project lead |
| **Vendor's own leadership / investors** | The vendor ROI picture — 12-month ROI is **−81%**; 36-month ROI is **−44%** at a realistic pace of 1 new client/year (3 total clients by end of Year 3). **3 clients alone does not make this business sustainable** — annual loss of ~€30,710 once founder pay is counted. **5 clients is the realistic target** for genuine margin (~€69,290/year) — at 1 client/year, that's Year 5, not Year 3. | Project lead / founder |
| **Compliance Officer** (internal) | Legal basis for crawling supplier sites, confirmation that no personal data is processed, audit-trail requirements — tied to risks R1 (EU AI Act classification) and R2 (data residency) in the risk register | Legal/Compliance lead, with the project lead |
| **Legal** (internal) | Liability position if an extracted field is wrong, web-scraping legality against supplier terms of use, EU AI Act transparency classification, and the IP boundary between extracting structured facts and reproducing supplier text — risks R3, R11 in the risk register | Legal lead |

---

## 5. Success Metrics per Phase

### 🟢 Client-Facing

**Phase 1 — already achieved:** 100% field extraction accuracy against verified ground truth on the five target combinations; zero fields requiring human review.

**Phase 2 — Pilot (Greenlight Criteria for Full Deployment):**
- ≥90% field coverage across your top 50 supplier/country combinations
- ≥95% extraction accuracy validated at that scale
- All three workshops completed and signed off by your content team
- ≥4 weeks of clean shadow mode — no serious errors found in the parallel run

If any of these aren't met, Full Deployment doesn't begin until they are.

**Phase 3 — Full Deployment:**
- Zero accuracy regression from shadow-mode results once live
- T&C updates reflected within 24 hours of a source document changing
- Under 5% of API responses falling back to "needs confirmation"
- Measurable reduction in T&C-related counter disputes with your customers

**Phase 4 — Expansion:**
- Coverage achieved for additional T&C fields and markets, against the same accuracy bar applied in Phase 2 and 3

---

### 🔒 Internal Only

**Phase 2 cost tracking:** the production build stays within the ROI's upfront cost envelope (€101,750–€172,950).

**Phase 3 cost tracking:** ongoing cost tracking against the ROI's €91,055 (months 7–12, incl. founder fee) and €180,710/year (Year 2–3, incl. founder fee and legal retainer) figures; case study published and used to begin signing additional clients at a realistic pace of ~1/year.

**Phase 4:** growth in paying client count and recurring revenue, narrowing the per-client cost-floor gap described in Section 3 (internal pricing rationale). Target: 5 total clients for genuine margin.

---

## 6. Commercialisation Model

### 🟢 Client-Facing

TermsIQ is provided as a **subscription data service (SaaS)** — not a one-time consulting deliverable and not software you'd need to build or maintain in-house. The value isn't a single extraction, it's the ongoing monitoring and re-extraction every time a supplier updates their T&C documents — which only makes sense as an ongoing relationship, not a one-off project.

In practice it's a hybrid of three elements, all described above:

1. **A one-time onboarding fee** covering the hands-on setup work specific to your organisation
2. **An annual subscription** for ongoing API access, daily change monitoring, and the human review interface
3. **A self-hosting licence option**, held in reserve for the specific case where your data-residency requirements rule out shared infrastructure

You are not asked to host anything, maintain any AI infrastructure, or manage the extraction pipeline. What stays with your team is the judgement call on anything flagged for review, and the decision of when to expand coverage.

---

### 🔒 Internal Only

TermsIQ is best positioned as a productised SaaS data layer rather than a consulting engagement or an internal tool. An internal tool doesn't fit: the buyer and user are an external company, and the go-to-market strategy is built around signing additional clients off one case study — which only makes sense for a product meant to scale across multiple customers. A pure consulting/services model doesn't fit either, because the core value is ongoing monitoring, not a one-time deliverable.

The Growth tier price (€50,000/year) is set from the vendor's actual fully-loaded cost base — including the founder's own pay — not from what would make the client's ROI look most attractive. At a realistic sales pace of one new client per year, the vendor's **36-month ROI is −44%** with 3 total clients reached by end of Year 3, and the business does not turn genuinely profitable until **5 clients** are signed — at this pace, that's roughly **Year 5**. No single pilot client's first-year subscription covers the build cost, and the business case depends on either the client base reaching 5 faster than one per year, or the founder planning for a longer runway than 3 years.

---

## 7. Compliance Position

### 🟢 Client-Facing

TermsIQ is classified **Limited Risk** under the EU AI Act (Article 50) — it extracts factual fields for B2B distribution and makes no individualised decisions about your customers. Your business remains responsible for how the data is displayed to your customers; TermsIQ's role is to ensure that data is accurate, current, and traceable.

Under GDPR, the core system processes no personal data — only supplier commercial documents. The single external data transfer (LLM-based extraction) is contractually restricted to EU infrastructure with zero-data-retention terms.

---

### 🔒 Internal Only

Full classification reasoning, gap tracking (G1–G5), and the DPIA/DPA structure are maintained in `eu_ai_act_compliance.md` and `gdpr_documentation.md`. This section intentionally summarises only the conclusion for client-facing use.

---

## 8. Next Step

### 🟢 Client-Facing

A 60-day pilot — your top 50 supplier/country combinations, shadow mode first, nothing live until your team has validated the results against real data.

---

*TermsIQ Strategic Deployment and Commercialisation Plan — Version 3.0 — June 2026*
*Cross-referenced against TermsIQ — ROI & Risk Assessment, Version 1.7*
*🟢 sections are client-distributable. 🔒 sections are for internal/evaluation use only and should be removed before external sharing.*
