# TermsIQ — Strategic Deployment Plan
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Prepared for [Client Name] · June 2026

---

## 1. Deployment Phases

### Phase 1 — Proven Capability (complete)

TermsIQ has already been validated across five real supplier/country combinations — extracting all five critical T&C fields (third-party liability cover, pickup grace period, licence rules, payment rules, cross-border conditions) with 100% field resolution and zero fields requiring human review. This is the working capability the rest of this plan builds on; it is not a concept, it is a measured result on real supplier documents.

### Phase 2 — Pilot (Months 1–6)

Your top 50 supplier/country combinations are mapped, configured, and run in shadow mode — TermsIQ's output is compared against your existing manual process for a minimum of four weeks, with nothing yet served to your OTA partners. Three structured workshops run during this phase:

- **Week 2 — Co-design:** defining the validation workflow and exception-handling rules together with your content team
- **Week 6 — Accuracy review:** reviewing real extraction-vs-source comparisons on your own documents
- **Week 10 — Impact review:** assessing readiness for go-live

Nothing goes live until your team has seen and approved the results against the Greenlight Criteria in Section 5.

### Phase 3 — Full Deployment (Month 7 onward)

The validated 50 combinations go live, and coverage expands toward your full supplier/country footprint — up to 250 combinations under the Growth tier (or further under Enterprise terms if your footprint is larger). From this point:

- T&C data is served live to your OTA partners via API
- Daily monitoring catches supplier document changes automatically, with updates reflected within 24 hours
- A case study is produced from your results, with your agreement on what's shared externally

### Phase 4 — Expansion (Year 2+, optional)

Coverage can grow beyond the original five fields and beyond your initial markets as your needs evolve — more supplier/country combinations, more T&C fields, more geographies, all under the same pricing structure described in Section 3.

---

## 2. Timeline and Milestones

| Phase | Timing | Milestone |
|---|---|---|
| Phase 1 — Proven Capability | Complete | 5/5 supplier/country combinations validated; 25/25 fields resolved; demo-ready |
| Phase 2 — Pilot | Months 1–6 | Source mapping and API integration complete (Week 1–2); co-design workshop (Week 2); accuracy review workshop (Week 6); impact review workshop (Week 10); ≥4-week clean shadow mode completed |
| Phase 3 — Full Deployment | Month 7 onward | Validated 50 combinations live; coverage expansion toward full footprint begins; case study published once results are measurable |
| Phase 4 — Expansion | Year 2+ (optional) | Additional T&C fields and markets added as agreed |

The single hard gate in this timeline is the end of Phase 2: Full Deployment does not begin until the Greenlight Criteria in Section 5 are met. Everything in Phase 3 onward assumes that gate has passed.

---

## 3. Go-to-Market and Commercial Approach

### Who this is for

TermsIQ is built for car rental aggregator API providers — typically 50–300 employees, managing connectivity for 100–500 suppliers, who are currently absorbing OTA partner complaints about T&C accuracy and facing EU consumer-law regulatory pressure. If that describes your business, the fit is direct rather than requiring adaptation.

### How the relationship works

This isn't a self-serve product — it's a direct, hands-on engagement, sized to a 2–4 month evaluation-to-decision window. The clearest way to evaluate it is the live demo: a real Hertz or Sixt T&C document, extracted in seconds, with full source attribution on every field — that's available before any commitment is made.

### Pricing model

| Tier | Coverage | Annual price |
|---|---|---|
| Pilot | 50 combinations, validated in shadow mode (Months 1–6) | Same rate as Growth tier from Month 7 — no markup, no hidden discount-then-increase |
| **Growth** | Up to 250 combinations | **€50,000/year** |
| Enterprise | 250+ combinations, multiple markets | €90,000+/year, custom terms |

Plus a one-time onboarding fee (€10,000–25,000, depending on scope) covering source mapping, API integration, and the three Phase 2 workshops.

A self-hosting licence option is available if your data-residency requirements rule out shared infrastructure.

**Source mapping is a shared task:** you provide the list of your target supplier/country combinations and whatever you already know about each document's location; the technical verification — confirming each source is reachable, classifying its format, configuring extraction — is handled for you.

### Why TermsIQ vs. the alternatives

**Against your current process** — a content team manually reading supplier PDFs — TermsIQ is faster and catches changes between review cycles that a manual process would miss.

**Against generic document-AI or OCR tools** — the differentiator is domain depth: extraction logic tuned to how each rental company actually structures its T&C documents, built-in resolution of statutory-minimum liability figures against the official COB reference table, and full field-level provenance on every output.

**Against building it yourself** — this is already a working, measured pipeline, not a from-scratch engineering project for your team to take on.

**Against doing nothing** — the regulatory environment makes this a live risk, not a hypothetical one. The EU Consumer Centres Network logged 6,016 complaints about car rental companies in 2025, and 55% of screened online intermediaries were found to violate EU consumer law on T&C transparency. The European Commission has already taken formal enforcement action against five major suppliers (2017–2020) for exactly this kind of clarity failure.

**On third-party liability specifically** — this is the field most likely to matter directly to your customers, not just your compliance team. Most OTAs today can only tell a customer "statutory minimum applies," which means nothing to someone comparing two rental options at checkout. Being able to state the real figure (e.g. "€70,000,000 personal injury cover in Spain," not "as required by law") turns a compliance field into a concrete trust signal at the point of sale — one a competitor can't match without the same capability behind it.

---

## 4. Stakeholder Communication

Different people in your organisation need different things from this engagement. This is what each role should expect to hear, and when.

| Your stakeholder | What they need to hear from us | When |
|---|---|---|
| **Executive sponsor** (CCO or equivalent) | The business case: the regulatory and reputational risk of the status quo (6,016 EU complaints in 2025, active EC enforcement environment), what Phase 2 proves before any live data is served, and the go/no-go decision point at the end of the pilot. No commitment to Full Deployment is required until results are in hand. | Kickoff; end of Phase 2 (pilot results); Phase 3 go-live decision |
| **Head of Supplier Partnerships** | How their day-to-day role shifts from manually chasing supplier T&C updates to exception management and supplier engagement once the system is live; what's needed from them at onboarding (the target combination list and known document sources) | Phase 1 kickoff; Phase 2 scoping, ongoing |
| **Content / Product Manager** | They co-design the validation workflow in Week 2, see real accuracy comparisons in Week 6, and own the day-to-day human review queue from Phase 3 onward — approving or correcting any field flagged below the confidence threshold before it reaches customers. The system is built to support their judgement, not replace it. | Throughout Phase 2 via the three workshops; ongoing from Phase 3 |
| **IT / Engineering lead (CTO or VP Engineering)** | The integration is additive, not a replacement for existing systems — T&C data is appended to the current API response, cached rather than computed per request, with sub-50ms added latency. A defined fallback (`data_not_available`) is returned for any field below confidence threshold, so nothing ambiguous reaches a live booking page. | Technical spec review before Phase 2 integration begins |
| **Legal / Compliance lead** | TermsIQ's EU AI Act classification (Limited Risk, Article 50), confirmation that no personal customer data is processed as part of the core function, and the data processing agreement covering the relationship, including disclosure of any sub-processors used | Before Phase 2 integration begins; reviewed again before any OTA contract references TermsIQ data |
| **OTA / channel partners** *(informed later, not part of internal rollout)* | Only once data-quality improvement is measurable — typically once the Phase 3 case study exists | Phase 3, once dispute-rate improvement and the case study are available |

---

## 5. Success Metrics per Phase

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

## 6. Commercialisation Model

TermsIQ is provided as a **subscription data service (SaaS)** — not a one-time consulting deliverable and not software you'd need to build or maintain in-house. The reasoning is straightforward: the value isn't a single extraction, it's the ongoing monitoring and re-extraction every time a supplier updates their T&C documents. That only makes sense as an ongoing relationship, not a one-off project.

In practice it's a hybrid of three elements, all described above:

1. **A one-time onboarding fee** covering the hands-on setup work specific to your organisation — source mapping, API integration, and the three Phase 2 workshops
2. **An annual subscription** for ongoing API access, daily change monitoring, and the human review interface — the recurring relationship that keeps your data current
3. **A self-hosting licence option**, held in reserve for the specific case where your data-residency requirements rule out shared infrastructure

You are not asked to host anything, maintain any AI infrastructure, or manage the extraction pipeline — that responsibility sits with us throughout the relationship. What stays with your team is the judgement call on anything flagged for review, and the decision of when to expand coverage.

---

## 7. Compliance Position

TermsIQ is classified **Limited Risk** under the EU AI Act (Article 50) — it extracts factual fields for B2B distribution and makes no individualised decisions about your customers. Your business remains responsible for how the data is displayed to your customers; TermsIQ's role is to ensure that data is accurate, current, and traceable.

Under GDPR, the core system processes no personal data — only supplier commercial documents. The single external data transfer (LLM-based extraction) is contractually restricted to EU infrastructure with zero-data-retention terms.

---

## 8. Next Step

A 60-day pilot — your top 50 supplier/country combinations, shadow mode first, nothing live until your team has validated the results against real data.

---

*TermsIQ — Strategic Deployment Plan*
*Prepared for [Client Name] — June 2026*
