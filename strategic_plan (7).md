# TermsIQ — Strategic Deployment and Commercialisation Plan
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 2.0 — June 2026

> This plan is built to read consistently alongside the *TermsIQ — ROI & Risk Assessment*. Phase timing, cost figures, and the pricing logic below all trace back to that document's numbers rather than introducing separate estimates — where a figure appears here, it's the same one the ROI uses.

---

## 1. Deployment Phases

### Phase 1 — Proof of Concept → MVP (current state, complete)

The project started as a single-document extraction pipeline validated across four supplier/country combinations, proving the core capability with measured accuracy against manually verified ground truth. The MVP extended this to five combinations and a multi-source resolution model, reaching 25/25 fields (100%) resolved, all auto-approved. This phase was built as a prototype — essentially zero hard cost, no contracted engineering team, no infrastructure spend — and its job was to prove the extraction approach works before committing real budget to it. **It is not the same thing as the "build" referenced in the ROI's upfront cost** — that figure (below) covers what comes next: turning this proven prototype into the production-grade system.

### Phase 2 — Pilot (Months 1–6)

This is the ROI's upfront-cost period — €137,350 (midpoint) over six months, covering the AI/NLP and backend engineering work to close the gaps catalogued in the MVP documentation (OCR for scanned documents, headless browser rendering for JS-only pages, a PostgreSQL knowledge base with version history, the human review interface, audit trail and compliance tooling), plus legal, GDPR, and EU AI Act review. Running alongside this build, one pilot client's top 50 supplier/country combinations go into shadow mode — TermsIQ's output compared against their existing manual process, not yet served to OTA partners — with a minimum four-week shadow period before anything goes live (per risk R5 in the ROI's risk register). The three content-team workshops (co-design, accuracy review, impact review) run on the Week 2 / Week 6 / Week 10 cadence within this window.

### Phase 3 — Full Deployment (Month 7 onward)

The system goes live — matching the ROI's own go-live assumption (A13: "Allows 6 months build + validation before production"). **Scope: the validated 50 combinations go live immediately, and the client begins expanding toward their full supplier/country footprint, up to the 250-combination ceiling of the Growth tier.** Full Deployment is not a continuation of the pilot's 50-combination scope — the pilot proves the system works; Full Deployment is when the client actually gets the value they're paying €50,000/year for, which is coverage of their real footprint, not just the validated subset. If a client's full footprint exceeds 250 combinations, they move to the Enterprise tier. The pilot client's TermsIQ output reaches their OTA partners for real, paying the **full Growth tier subscription rate from this point — no discount.** Ongoing cost from this point is €91,055 (midpoint) for the first six live months, rising to €180,710/year (midpoint, including a real founder/consultant fee and a legal/compliance retainer) from Year 2 once a full year of ongoing maintenance, monitoring, and the annual annotation-base review are all running. A case study is produced from this client's results and used to close additional clients over time.

### Phase 4 — Scale / Expansion *(optional, Year 2+)*

More clients, using the Phase 3 case study as the primary sales asset, and more coverage per client — additional T&C fields beyond the original five, and additional supplier/country combinations beyond the initial Spain/Germany focus. **This phase is not optional growth — it is required for the business to reach sustainable margin.** At 3 clients (the Phase 3 target), the business runs at an annual loss of roughly €30,710 once the founder's own pay is counted as a real cost. 5 clients is the realistic minimum scale at which the business covers its full cost base and starts generating genuine margin (~€69,290/year at 5 clients).

---

## 2. Timeline

| Phase | Timing | Cost (ROI midpoint) | Key milestones |
|---|---|---|---|
| Phase 1 — POC → MVP | Complete | ~€0 (prototype) | 5/5 supplier/country combinations; 25/25 field accuracy; demo-ready |
| Phase 2 — Pilot | Months 1–6 | €137,350 upfront | Production-grade build; pilot client's top 50 combinations in shadow mode; 3 workshops; ≥4-week shadow validation before go-live |
| Phase 3 — Full Deployment | Month 7 onward | €91,055 (months 7–12, incl. founder fee) | Validated 50 combinations go live; client expands toward full footprint (up to 250 under Growth tier); pilot client pays full Growth tier rate (no discount); case study published |
| Phase 4 — Scale *(required for sustainability, not optional)* | Year 2+ | €180,710/year (incl. founder fee + legal retainer) | Additional T&C fields in production; expansion beyond ES/DE; client base must reach 5 for genuine margin |

### What the vendor ROI says about this timeline, stated plainly

The 12-month vendor ROI is **−81%** — expected, because the build cost is concentrated in Year 1 and only one client (the pilot, paying the full Growth tier rate from Month 7 — no discount) is generating revenue. Revenue grows steadily at a realistic pace of **one new client signed per year** from Year 2 onward — not two clients simultaneously, which would be an optimistic assumption for a 2–4 month sales cycle with a small founding team. By the end of Year 3, this reaches 3 total paying clients: annual subscription revenue of €150,000 against ongoing costs of €180,710/year — **still a loss of roughly €30,710/year at 3 clients.** This is the central finding of the revised model: 3 clients, even at a properly cost-based price, is not enough for the business to be sustainable. **5 clients is the realistic minimum** — at that scale, revenue (€250,000) clears the full cost base (€180,710) with genuine margin (~€69,290/year). At a 1-client-per-year pace, 5 clients isn't reached until roughly **Year 5** — which means either the sales pace needs to accelerate beyond one client per year, or the founder should plan for a longer runway than 3 years before this is comfortably self-sustaining.

The Growth tier price of €50,000/year was deliberately built bottom-up from the vendor's actual fully-loaded cost base — including a real founder/consultant fee (previously absent from this model) and a legal/compliance retainer — rather than being set low to make the client's ROI look more dramatic. The client's case remains strong at this price (see the ROI document's Part B), so there was no need to underprice the product.

This plan doesn't soften the investment picture. Year 1 is a cost year by design — the system isn't live and generating subscription revenue until Month 7, and even though the pilot client pays the same full Growth tier rate as every other client from go-live, one client's revenue cannot offset the build cost. The business case rests on reaching 5 paying clients by the end of Phase 4, not 3 — this is the single most important number for any investor or stakeholder conversation about this plan's viability.

---

## 3. Go-to-Market Strategy

### Target buyers / customers

The primary buyer is the Chief Commercial Officer or Head of Supplier Partnerships at a car rental aggregator API provider — typically 50–300 employees, managing connectivity for 100–500 suppliers, currently absorbing OTA partner complaints about T&C accuracy and facing EU consumer-law regulatory pressure. The technical evaluator is the CTO or VP Engineering, who needs confidence that TermsIQ appends fields to the existing API response rather than replacing it, with an acceptable latency profile and a defined fallback behaviour. The day-to-day user is the Content or Product Manager who currently owns manual T&C maintenance — their adoption determines whether data quality actually improves after rollout, which is why they're engaged as a co-designer in Phase 2 rather than informed after the fact.

### Sales channel

Direct, B2B, sales-led — not self-serve. The decision is made at CCO/CTO level with a typical sales cycle of 2–4 months. The single most effective sales moment is a live demo: uploading a real Hertz or Sixt T&C PDF and watching the structured extraction complete in seconds, with full source attribution shown for every field.

### Pricing model

Three models apply here, each fitting a different client situation, plus a real per-use cost figure that explains why none of them should be priced on a per-extraction basis.

**1. SaaS subscription — recommended primary model.** Tiered by the number of active supplier/country combinations under coverage. This is the model that should carry most clients, and it is sized against the ROI's actual fully-loaded ongoing cost rather than an arbitrary figure or a price picked to flatter the client's ROI. The ongoing cost base is €180,710/year (midpoint, Year 2–3, including a real founder/consultant fee and a legal/compliance retainer, alongside the engineering, infrastructure, and monitoring costs). At 3 clients, splitting that cost three ways means each client needs to clear roughly €60,237/year just to cover its share of ongoing cost — before any margin, which is why 3 clients alone does not make this business sustainable. At **5 clients**, the realistic minimum scale, the per-client cost floor drops to roughly €36,142/year, leaving room for the tier price below to generate real margin:

| Tier | Coverage | Indicative annual price | Rationale |
|---|---|---|---|
| Pilot | 50 combinations validated in shadow mode (Months 1–6) | Same as Growth tier (€50,000/year) — no discount, from Month 7 | The pilot client pays the full rate from go-live; the "investment" in the case study is the discount-free 6 months of onboarding and shadow mode, not a reduced subscription. Scope expands beyond 50 once Full Deployment begins — see Phase 3 |
| Growth | Up to 250 combinations | **€50,000/year** | Set bottom-up from the actual cost base; clears the per-client cost floor at 5 clients with genuine margin; client ROI is strongly positive from Year 2 (Year 1 −21% while the system ramps; 36-month +74%) |
| Enterprise | 250+ combinations, multiple markets | €90,000+/year, custom terms | Larger clients carry a proportionally larger share of the shared cost base |

These are still estimates, not contracted prices — but they are now sized against a real, fully-loaded cost floor that includes the founder's own pay, not just external contractor and infrastructure bills.

**2. Consulting / implementation fee — per-client onboarding, alongside the subscription.** The Phase 2 onboarding work specific to each client — source mapping, API integration support, and the three content-team workshops — is billed as a one-time fee separate from the recurring subscription, in the €10,000–25,000 range depending on how many supplier/country combinations need mapping at onboarding. **Source mapping is a shared task, not something either side does alone:** the client's content team provides the list of their target supplier/country combinations and whatever they already know about each document's location (a URL, a contact, a shared file); the vendor's team then does the technical verification — confirming each source is reachable, classifying its format (PDF, web, Excel, JS-rendered), and configuring the extraction hints it needs. This keeps the subscription price clean and predictable while still covering the real, client-specific setup cost; it's a smaller, per-client slice of the same kind of work the ROI's upfront change-management line items (training, supplier communication, stakeholder workshops) cover at the platform level.

**3. Licence — for clients with strict data-residency or self-hosting requirements.** TermsIQ's own infrastructure is built for German data residency, but a large enterprise client may have its own residency or self-hosting requirements that a shared multi-tenant SaaS platform can't satisfy. For these clients, an annual or perpetual licence to run the TermsIQ pipeline within their own infrastructure is the right model — a larger upfront licence fee plus a smaller ongoing support/update fee, with hosting cost shifting to the client. This is a secondary option for a specific class of enterprise buyer, not the default.

**Per-use cost — why it isn't a standalone pricing model.** With the MVP now live, there's real data on this rather than a projection. Across the actual GPT-4o-mini extraction runs from this session — the same five supplier/country combinations, nine total LLM calls — total token usage was 33,191 tokens for a complete initial extraction batch. At GPT-4o-mini's actual pricing ($0.15 per million input tokens, $0.60 per million output tokens), that's roughly **€0.006 for the entire five-combination batch**, or about **€0.0012 per supplier/country combination**. Scaled up, a 50-combination pilot's full initial batch costs roughly €0.06 in API calls; a 250-combination Growth-tier client's batch costs roughly €0.30. This confirms — with real numbers now, on the actual model deployed, rather than the original vision-stage estimate built on Claude Sonnet pricing — that the AI API cost is not the cost driver behind this product. A genuine per-use price would be too small to matter on its own; charging meaningfully more than this per extraction would just be an indirect, poorly-labelled way of recovering the people, infrastructure, and compliance cost that the subscription tiers above are already sized to cover directly. Per-use cost is useful evidence for why the subscription model is priced the way it is — it isn't a pricing model in its own right.

### Key differentiator vs. alternatives

Against the status quo — a content team manually reading PDFs — TermsIQ is faster and catches changes the manual process would miss between review cycles. Against generic document-AI or OCR platforms, the differentiator is domain depth: per-supplier extraction hints tuned to how each rental company actually structures its documents, built-in resolution of the statutory-minimum TPL question against the COB reference table, and full field-level provenance on every output. Against building it in-house, TermsIQ already has a working, measured pipeline rather than asking the client to start from zero. And against doing nothing, the ROI's own numbers make the regulatory case concrete rather than abstract: a 10%-per-year probability of EU enforcement action, at €50,000–500,000 exposure if it materialises — a risk most aggregators are currently carrying unpriced.

**TPL specifically is the sharpest edge of this, and it's a customer-facing one, not just a compliance one.** Most OTAs today can only tell a customer "statutory minimum applies" — which means nothing to someone comparing two rental options at checkout. An OTA that can instead state the real number (€70,000,000 personal injury cover in Spain, not "as required by law") turns a compliance field into a concrete trust signal at the point of sale, one a competitor can't match without the same COB-resolution capability behind it. This is the field most likely to actually appear in an OTA's own marketing copy, not just in their terms page — which is also why it's the field most worth getting right: an inaccurate or fabricated TPL figure shown to a customer is the highest-stakes version of the R4 hallucination risk in the ROI document, since it's a number a customer might actually rely on when choosing where to book.

---

## 4. Stakeholder Communication Plan

| Stakeholder | What they need to know | Who communicates | When |
|---|---|---|---|
| **Chief Commercial Officer** (primary sponsor) | The vendor ROI picture — 12-month ROI is −81% (investment year; the pilot client pays the full subscription rate from Month 7, same as every client — no discount); 36-month ROI is **−44%** at a realistic pace of 1 new client signed per year (3 total clients by end of Year 3). **3 clients alone does not make this business sustainable** — at 3 clients the business runs at an annual loss of ~€30,710 once the founder's own pay is counted as a real cost. **5 clients is the realistic target** for genuine margin (~€69,290/year) — at a 1-client-per-year pace, that's roughly Year 5, not Year 3. Pilot results to inform the Phase 3 go/no-go and whether the sales pace can realistically exceed 1 client/year. | Project lead | Phase 1 kickoff; end of Phase 2 (pilot results); Phase 3 go-live decision |
| **Head of Supplier Partnerships** | How their role shifts from manually chasing supplier T&C updates to exception management and supplier engagement; provides the list of target supplier/country combinations and known document sources at onboarding — the vendor's team then verifies and configures each source technically | Project lead | Phase 1 (role definition); Phase 2 (pilot scoping, ongoing) |
| **Content / Product Manager** | Must co-design the validation workflow and exception-handling rules during Phase 2, and **owns the human review queue on an ongoing basis from Phase 3 onward** — they are the ones who check flagged low-confidence fields against the source document and approve or correct them. TermsIQ provides and maintains the review interface and tunes the confidence threshold so the right fields get routed there; the client's content team makes the actual approve/correct decisions. This is the risk the ROI flags as R7 (content team adoption), the risk most likely to be underestimated | Project lead, via three structured workshops: co-design (Week 2), accuracy review (Week 6), impact review (Week 10) | Throughout Phase 2; ongoing review queue ownership from Phase 3 |
| **Head of Engineering / CTO** | The integration contract is additive, not breaking; T&C data is cached rather than computed per request; the confidence-score mechanism and the "serve nothing rather than serve wrong" fallback policy that mitigates R4 (the ROI's highest-rated risk — LLM hallucination reaching a customer) | Engineering lead | Phase 1 (technical spec review); before Phase 2 integration begins |
| **OTA / Channel partners** *(indirect)* | Informed only once data-quality improvement is measurable — not part of internal rollout communications | CCO / account management team | Phase 3, once dispute-rate data and the case study exist |
| **Compliance Officer** | Legal basis for crawling supplier sites, confirmation that no personal data is processed, audit-trail and version-history requirements, and the documented confidence-threshold policy — directly tied to risks R1 (EU AI Act classification) and R2 (data residency) in the ROI's risk register | Legal/Compliance lead, with the project lead | Before any web crawling goes live in Phase 2 |
| **Legal** | Liability position if an extracted field is wrong, web-scraping legality against supplier terms of use, EU AI Act transparency classification, and the IP boundary between extracting structured facts and reproducing supplier text — risks R3, R11 in the ROI's risk register | Legal lead | Before Phase 2 crawling goes live; before any OTA contract references TermsIQ data fields in Phase 3 |

---

## 5. Key Performance Indicators per Phase

**Phase 1 — POC → MVP:** field extraction accuracy against ground truth (target ≥95%, achieved 100% on 25/25); field coverage across the five target combinations (achieved 5/5); human-review rate (achieved 0% — all auto-approved); a working, demo-ready pipeline on real supplier documents.

**Phase 2 — Pilot (Months 1–6):** the production build stays within the ROI's upfront cost envelope (€101,750–€172,950); field coverage across ≥90% of the pilot client's top 50 active supplier/country combinations; extraction accuracy ≥95% at that larger scale; all three content-manager workshops completed and signed off; minimum four-week shadow mode completed before go-live.

**Phase 3 — Full Deployment (Month 7 onward):** the validated 50 combinations go live with zero regression from shadow-mode accuracy; client begins expansion toward their full supplier/country footprint (up to 250 combinations under the Growth tier), with the same ≥90% coverage / ≥95% accuracy bar applied as combinations are added; ongoing cost tracking against the ROI's €91,055 (months 7–12, incl. founder fee) and €180,710/year (Year 2–3, incl. founder fee and legal retainer) figures; T&C updates reflected within 24 hours of a source document changing; ≤50ms additional API latency; under 5% of API responses falling back to "needs confirmation"; measurable reduction in T&C-related counter disputes; case study published and used to begin signing additional clients at a realistic pace of ~1/year.

**Phase 4 — Scale:** coverage achieved for additional T&C fields beyond the original five; expansion beyond the initial Spain/Germany market focus; growth in paying client count and recurring revenue, narrowing the per-client cost-floor gap described in the pricing section above.

---

## 6. Commercialisation Model

TermsIQ is best positioned as a productised SaaS data layer — an API add-on sold to car rental aggregator providers — rather than a consulting engagement or an internal tool. An internal tool doesn't fit: the buyer and user are an external company, and the go-to-market strategy is explicitly built around signing a second and third client off one case study, which only makes sense for a product meant to scale across multiple customers. A pure consulting/services model doesn't fit either, because TermsIQ's core value isn't a one-time deliverable — it's ongoing monitoring and re-extraction as supplier documents change, which only pays for itself as a recurring relationship.

In practice the model is a hybrid of the three pricing components above, not pure self-serve SaaS from day one: a real consulting/services component at onboarding (Phase 2's white-glove build and workshops), the recurring SaaS subscription as the long-term relationship from Phase 3 onward at the same rate for every client including the pilot, and a licence option held in reserve for the subset of enterprise clients whose data-residency requirements rule out shared infrastructure. The Growth tier price (€50,000/year) is set from the vendor's actual fully-loaded cost base — including the founder's own pay — not from what would make the client's ROI look most attractive. At a realistic sales pace of one new client per year, the vendor's 36-month ROI is **−44%** with 3 total clients reached by end of Year 3, and the business does not turn genuinely profitable until **5 clients** are signed — at this pace, that's roughly Year 5. No single pilot client's first-year subscription covers the build cost, and the business case depends on either the client base reaching 5 faster than one per year, or the founder planning for a longer runway than 3 years.

---

*TermsIQ Strategic Deployment and Commercialisation Plan — Version 2.7 — June 2026*
*Cross-referenced against TermsIQ — ROI & Risk Assessment, Version 1.7 (steady 1-client-per-year acquisition pace)*
