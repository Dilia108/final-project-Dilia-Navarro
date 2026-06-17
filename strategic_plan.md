# TermsIQ — Strategic Deployment and Commercialisation Plan
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 2.0 — June 2026

> This plan is built to read consistently alongside the *TermsIQ — ROI & Risk Assessment*. Phase timing, cost figures, and the pricing logic below all trace back to that document's numbers rather than introducing separate estimates — where a figure appears here, it's the same one the ROI uses.

---

## 1. Deployment Phases

### Phase 1 — Proof of Concept → MVP (current state, complete)

The project started as a single-document extraction pipeline validated across four supplier/country combinations, proving the core capability with measured accuracy against manually verified ground truth. The MVP extended this to five combinations and a multi-source resolution model, reaching 25/25 fields (100%) resolved, all auto-approved. This phase was built as a prototype — essentially zero hard cost, no contracted engineering team, no infrastructure spend — and its job was to prove the extraction approach works before committing real budget to it. **It is not the same thing as the "build" referenced in the ROI's upfront cost** — that figure (below) covers what comes next: turning this proven prototype into the production-grade system.

### Phase 2 — Pilot (Months 1–6)

This is the ROI's upfront-cost period — €143,000 (midpoint) over six months, covering the AI/NLP and backend engineering work to close the gaps catalogued in the MVP documentation (OCR for scanned documents, headless browser rendering for JS-only pages, a PostgreSQL knowledge base with version history, the human review interface, audit trail and compliance tooling), plus legal, GDPR, and EU AI Act review. Running alongside this build, one pilot client's top 50 supplier/country combinations go into shadow mode — TermsIQ's output compared against their existing manual process, not yet served to OTA partners — with a minimum four-week shadow period before anything goes live (per risk R5 in the ROI's risk register). The three content-team workshops (co-design, accuracy review, impact review) run on the Week 2 / Week 6 / Week 10 cadence within this window.

### Phase 3 — Full Deployment (Month 7 onward)

The system goes live — matching the ROI's own go-live assumption (A13: "Allows 6 months build + validation before production"). The pilot client's TermsIQ output reaches their OTA partners for real. Ongoing cost from this point is €67,205 (midpoint) for the first six live months, rising to €133,010/year (midpoint) from Year 2 once a full year of ongoing maintenance, monitoring, and the annual annotation-base review are all running. A case study is produced from this client's results and used to close a second and third client.

### Phase 4 — Scale / Expansion *(optional, Year 2+)*

More clients, using the Phase 3 case study as the primary sales asset, and more coverage per client — additional T&C fields beyond the original five, and additional supplier/country combinations beyond the initial Spain/Germany focus.

---

## 2. Timeline

| Phase | Timing | Cost (ROI midpoint) | Key milestones |
|---|---|---|---|
| Phase 1 — POC → MVP | Complete | ~€0 (prototype) | 5/5 supplier/country combinations; 25/25 field accuracy; demo-ready |
| Phase 2 — Pilot | Months 1–6 | €143,000 upfront | Production-grade build; pilot client's top 50 combinations in shadow mode; 3 workshops; ≥4-week shadow validation before go-live |
| Phase 3 — Full Deployment | Month 7 onward | €67,205 (months 7–12) | Pilot client live in production API; case study published; 2nd and 3rd client signed |
| Phase 4 — Scale *(optional)* | Year 2+ | €133,010/year | Additional T&C fields in production; expansion beyond ES/DE; client base beyond the first three |

### What the ROI says about this timeline, stated plainly

The 12-month ROI is **−90%**; the 36-month ROI is **−78%** on quantified cost-saving streams alone, or **−59%** including the commercial-differentiation upside. Break-even sits at month 67 (base case) or month 48 with the commercial upside included — both multi-year horizons. This plan doesn't soften that. Year 1 is an investment year by design: the system isn't live generating value until month 7, and the value streams that are easiest to quantify (customer service cost reduction, risk-adjusted regulatory exposure avoidance) are deliberately conservative. The case for proceeding rests less on a fast payback and more on two things the ROI document is explicit about: a single EU regulatory enforcement action, which the ROI estimates at €50,000–500,000 in exposure, would justify the entire build cost in one incident and pulls break-even down to 18–24 months; and the commercial differentiation argument (Phase 4's client growth) compounds in a way the conservative base case doesn't capture.

---

## 3. Go-to-Market Strategy

### Target buyers / customers

The primary buyer is the Chief Commercial Officer or Head of Supplier Partnerships at a car rental aggregator API provider — typically 50–300 employees, managing connectivity for 100–500 suppliers, currently absorbing OTA partner complaints about T&C accuracy and facing EU consumer-law regulatory pressure. The technical evaluator is the CTO or VP Engineering, who needs confidence that TermsIQ appends fields to the existing API response rather than replacing it, with an acceptable latency profile and a defined fallback behaviour. The day-to-day user is the Content or Product Manager who currently owns manual T&C maintenance — their adoption determines whether data quality actually improves after rollout, which is why they're engaged as a co-designer in Phase 2 rather than informed after the fact.

### Sales channel

Direct, B2B, sales-led — not self-serve. The decision is made at CCO/CTO level with a typical sales cycle of 2–4 months. The single most effective sales moment is a live demo: uploading a real Hertz or Sixt T&C PDF and watching the structured extraction complete in seconds, with full source attribution shown for every field.

### Pricing model

Three models apply here, each fitting a different client situation, plus a real per-use cost figure that explains why none of them should be priced on a per-extraction basis.

**1. SaaS subscription — recommended primary model.** Tiered by the number of active supplier/country combinations under coverage. This is the model that should carry most clients, and it can now be sized against the ROI's actual ongoing cost rather than an arbitrary figure. The ongoing cost base is €133,010/year (midpoint, Year 2–3, including the annotation-maintenance line). At the Phase 3 target of three paying clients, splitting that cost three ways means each client needs to clear roughly €44,237/year just to cover its share of ongoing cost — before any margin. By Phase 4, with six or more clients sharing a cost base that doesn't scale linearly with client count, that floor drops to roughly €22,000/year per client, which is where margin starts to build. Tier pricing should sit comfortably above the Phase 3 floor:

| Tier | Coverage | Indicative annual price | Rationale |
|---|---|---|---|
| Pilot | Up to 50 combinations | Discounted or waived during Phase 2, converting to a paid tier at Phase 3 go-live | Investment in the case study, not a revenue line yet |
| Growth | Up to 250 combinations | €60,000–90,000/year | Clears the ~€44k Phase-3 cost floor with real margin even with only 3 clients on the books |
| Enterprise | 250+ combinations, multiple markets | €120,000+/year, custom terms | Larger clients carry a proportionally larger share of the shared cost base and the human-review/monitoring load that scales with coverage |

These are still estimates, not contracted prices — but unlike the previous version of this plan, they're now sized against a real cost floor instead of being picked arbitrarily.

**2. Consulting / implementation fee — per-client onboarding, alongside the subscription.** The Phase 2 onboarding work specific to each client — source mapping for their particular supplier base, API integration support, and the three content-team workshops — is billed as a one-time fee separate from the recurring subscription, in the €10,000–25,000 range depending on how many supplier/country combinations need mapping at onboarding. This keeps the subscription price clean and predictable while still covering the real, client-specific setup cost; it's a smaller, per-client slice of the same kind of work the ROI's upfront change-management line items (training, supplier communication, stakeholder workshops) cover at the platform level.

**3. Licence — for clients with strict data-residency or self-hosting requirements.** TermsIQ's own infrastructure is built for German data residency, but a large enterprise client may have its own residency or self-hosting requirements that a shared multi-tenant SaaS platform can't satisfy. For these clients, an annual or perpetual licence to run the TermsIQ pipeline within their own infrastructure is the right model — a larger upfront licence fee plus a smaller ongoing support/update fee, with hosting cost shifting to the client. This is a secondary option for a specific class of enterprise buyer, not the default.

**Per-use cost — why it isn't a standalone pricing model.** With the MVP now live, there's real data on this rather than a projection. Across the actual GPT-4o-mini extraction runs from this session — the same five supplier/country combinations, nine total LLM calls — total token usage was 33,191 tokens for a complete initial extraction batch. At GPT-4o-mini's actual pricing ($0.15 per million input tokens, $0.60 per million output tokens), that's roughly **€0.006 for the entire five-combination batch**, or about **€0.0012 per supplier/country combination**. Scaled up, a 50-combination pilot's full initial batch costs roughly €0.06 in API calls; a 250-combination Growth-tier client's batch costs roughly €0.30. This confirms — with real numbers now, on the actual model deployed, rather than the original vision-stage estimate built on Claude Sonnet pricing — that the AI API cost is not the cost driver behind this product. A genuine per-use price would be too small to matter on its own; charging meaningfully more than this per extraction would just be an indirect, poorly-labelled way of recovering the people, infrastructure, and compliance cost that the subscription tiers above are already sized to cover directly. Per-use cost is useful evidence for why the subscription model is priced the way it is — it isn't a pricing model in its own right.

### Key differentiator vs. alternatives

Against the status quo — a content team manually reading PDFs — TermsIQ is faster and catches changes the manual process would miss between review cycles. Against generic document-AI or OCR platforms, the differentiator is domain depth: per-supplier extraction hints tuned to how each rental company actually structures its documents, built-in resolution of the statutory-minimum TPL question against the COB reference table, and full field-level provenance on every output. Against building it in-house, TermsIQ already has a working, measured pipeline rather than asking the client to start from zero. And against doing nothing, the ROI's own numbers make the regulatory case concrete rather than abstract: a 10%-per-year probability of EU enforcement action, at €50,000–500,000 exposure if it materialises — a risk most aggregators are currently carrying unpriced.

**TPL specifically is the sharpest edge of this, and it's a customer-facing one, not just a compliance one.** Most OTAs today can only tell a customer "statutory minimum applies" — which means nothing to someone comparing two rental options at checkout. An OTA that can instead state the real number (€70,000,000 personal injury cover in Spain, not "as required by law") turns a compliance field into a concrete trust signal at the point of sale, one a competitor can't match without the same COB-resolution capability behind it. This is the field most likely to actually appear in an OTA's own marketing copy, not just in their terms page — which is also why it's the field most worth getting right: an inaccurate or fabricated TPL figure shown to a customer is the highest-stakes version of the R4 hallucination risk in the ROI document, since it's a number a customer might actually rely on when choosing where to book.

---

## 4. Stakeholder Communication Plan

| Stakeholder | What they need to know | Who communicates | When |
|---|---|---|---|
| **Chief Commercial Officer** (primary sponsor) | The honest ROI picture — negative on cost-saving streams alone through Year 3, with break-even realistically 4–5.5 years out, but a single avoided regulatory action (€50k–500k exposure) or the commercial-differentiation upside changes that materially; pilot results to inform the Phase 3 go/no-go | Project lead | Phase 1 kickoff; end of Phase 2 (pilot results); Phase 3 go-live decision |
| **Head of Supplier Partnerships** | How their role shifts from manually chasing supplier T&C updates to exception management and supplier engagement; involved in choosing which supplier/country combinations enter the pilot | Project lead | Phase 1 (role definition); Phase 2 (pilot scoping, ongoing) |
| **Content / Product Manager** | Must co-design the validation workflow and exception-handling rules, and needs to see real extraction-vs-source comparisons before trusting the system in production — this is the risk the ROI flags as R7 (content team adoption), the risk most likely to be underestimated | Project lead, via three structured workshops: co-design (Week 2), accuracy review (Week 6), impact review (Week 10) | Throughout Phase 2 |
| **Head of Engineering / CTO** | The integration contract is additive, not breaking; T&C data is cached rather than computed per request; the confidence-score mechanism and the "serve nothing rather than serve wrong" fallback policy that mitigates R4 (the ROI's highest-rated risk — LLM hallucination reaching a customer) | Engineering lead | Phase 1 (technical spec review); before Phase 2 integration begins |
| **OTA / Channel partners** *(indirect)* | Informed only once data-quality improvement is measurable — not part of internal rollout communications | CCO / account management team | Phase 3, once dispute-rate data and the case study exist |
| **Compliance Officer** | Legal basis for crawling supplier sites, confirmation that no personal data is processed, audit-trail and version-history requirements, and the documented confidence-threshold policy — directly tied to risks R1 (EU AI Act classification) and R2 (data residency) in the ROI's risk register | Legal/Compliance lead, with the project lead | Before any web crawling goes live in Phase 2 |
| **Legal** | Liability position if an extracted field is wrong, web-scraping legality against supplier terms of use, EU AI Act transparency classification, and the IP boundary between extracting structured facts and reproducing supplier text — risks R3, R11 in the ROI's risk register | Legal lead | Before Phase 2 crawling goes live; before any OTA contract references TermsIQ data fields in Phase 3 |

---

## 5. Key Performance Indicators per Phase

**Phase 1 — POC → MVP:** field extraction accuracy against ground truth (target ≥95%, achieved 100% on 25/25); field coverage across the five target combinations (achieved 5/5); human-review rate (achieved 0% — all auto-approved); a working, demo-ready pipeline on real supplier documents.

**Phase 2 — Pilot (Months 1–6):** the production build stays within the ROI's upfront cost envelope (€101,750–€172,950); field coverage across ≥90% of the pilot client's top 50 active supplier/country combinations; extraction accuracy ≥95% at that larger scale; all three content-manager workshops completed and signed off; minimum four-week shadow mode completed before go-live.

**Phase 3 — Full Deployment (Month 7 onward):** ongoing cost tracking against the ROI's €67,205 (months 7–12) and €133,010/year (Year 2–3) figures; T&C updates reflected within 24 hours of a source document changing; ≤50ms additional API latency; under 5% of API responses falling back to "needs confirmation"; measurable reduction in T&C-related counter disputes; second and third client signed off the case study.

**Phase 4 — Scale:** coverage achieved for additional T&C fields beyond the original five; expansion beyond the initial Spain/Germany market focus; growth in paying client count and recurring revenue, narrowing the per-client cost-floor gap described in the pricing section above.

---

## 6. Commercialisation Model

TermsIQ is best positioned as a productised SaaS data layer — an API add-on sold to car rental aggregator providers — rather than a consulting engagement or an internal tool. An internal tool doesn't fit: the buyer and user are an external company, and the go-to-market strategy is explicitly built around signing a second and third client off one case study, which only makes sense for a product meant to scale across multiple customers. A pure consulting/services model doesn't fit either, because TermsIQ's core value isn't a one-time deliverable — it's ongoing monitoring and re-extraction as supplier documents change, which only pays for itself as a recurring relationship.

In practice the model is a hybrid of the three pricing components above, not pure self-serve SaaS from day one: a real consulting/services component at onboarding (Phase 2's white-glove build and workshops), the recurring SaaS subscription as the long-term relationship from Phase 3 onward, and a licence option held in reserve for the subset of enterprise clients whose data-residency requirements rule out shared infrastructure. The ROI's own numbers are the honest reason this has to be a multi-year commercial relationship rather than a quick sale: at a 67-month base-case break-even, no single pilot client's first-year subscription fee comes close to covering the build cost, and the business case depends on a client base building over Phase 3 and Phase 4, not on Phase 2 alone being profitable.

---

*TermsIQ Strategic Deployment and Commercialisation Plan — Version 2.0 — June 2026*
*Cross-referenced against TermsIQ — ROI & Risk Assessment, Version 1.4*
