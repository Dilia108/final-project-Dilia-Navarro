# TermsIQ — Deployment Plan
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Prepared for [Client Name] · June 2026

---

## 1. Deployment Phases

### Phase 1 — Proven Capability (complete)

TermsIQ has already been validated across five real supplier/country combinations — extracting all five critical T&C fields (third-party liability cover, pickup grace period, licence rules, payment rules, cross-border conditions) with 100% field resolution and zero fields requiring human review. This is the working capability the rest of this plan builds on.

### Phase 2 — Onboarding & Shadow Mode (Months 1–6)

Your top 50 supplier/country combinations are mapped and configured. TermsIQ runs in parallel with your existing manual process for a minimum of four weeks — comparing its output against what your content team already knows, with nothing yet served to your OTA partners. Three structured workshops run during this phase:

- **Week 2 — Co-design:** defining the validation workflow and exception-handling rules together
- **Week 6 — Accuracy review:** reviewing real extraction-vs-source comparisons on your own documents
- **Week 10 — Impact review:** assessing readiness for go-live

Nothing goes live until your team has seen and approved the results.

### Phase 3 — Full Deployment (Month 7 onward)

The validated 50 combinations go live, and coverage expands toward your full supplier/country footprint — up to 250 combinations under the Growth tier (or further under Enterprise terms if your footprint is larger). From this point:

- T&C data is served live to your OTA partners via API
- Daily monitoring catches supplier document changes automatically
- A case study is produced from your results, with your agreement on what's shared

### Phase 4 — Expansion (Year 2+, optional)

Coverage can grow beyond the original five fields and beyond your initial markets, as your needs evolve — more supplier/country combinations, more T&C fields, more geographies.

---

## 2. What You Get

| Capability | Detail |
|---|---|
| **Structured T&C data via API** | Five critical fields per supplier/country combination, appended to your existing API response — not a replacement integration |
| **Daily change monitoring** | Supplier documents are checked daily; updates are reflected within 24 hours |
| **Human review gate** | Any field below a confidence threshold is held for your content team to review before it goes live — nothing reaches your customers unverified |
| **Full source attribution** | Every field carries the source document, extraction timestamp, and confidence score, so your team can verify anything in seconds |
| **No breaking changes** | The integration is additive — your existing systems and data flows are unaffected |

---

## 3. Why TermsIQ vs. the Alternatives

**Against your current process** — a content team manually reading supplier PDFs — TermsIQ is faster and catches changes between review cycles that a manual process would miss.

**Against generic document-AI or OCR tools** — the differentiator is domain depth: extraction logic tuned to how each rental company actually structures its T&C documents, built-in resolution of statutory-minimum liability figures against the official COB reference table, and full field-level provenance on every output.

**Against building it yourself** — TermsIQ is already a working, measured pipeline, not a from-scratch engineering project for your team to take on.

**Against doing nothing** — the regulatory environment makes this a live risk, not a hypothetical one. The EU Consumer Centres Network logged 6,016 complaints about car rental companies in 2025, and 55% of screened online intermediaries were found to violate EU consumer law on T&C transparency. The European Commission has already taken formal enforcement action against five major suppliers (2017–2020) for exactly this kind of clarity failure.

**On third-party liability specifically** — this is the field most likely to matter directly to your customers, not just your compliance team. Most OTAs today can only tell a customer "statutory minimum applies," which means nothing to someone comparing two rental options at checkout. Being able to state the real figure (e.g. "€70,000,000 personal injury cover in Spain," not "as required by law") turns a compliance field into a concrete trust signal at the point of sale.

---

## 4. Greenlight Criteria — Pilot to Full Deployment

Before Phase 3 begins, four conditions must be met:

- **≥90% field coverage** across your top 50 supplier/country combinations
- **≥95% extraction accuracy** validated at that scale
- **All three workshops** completed and signed off by your content team
- **≥4 weeks of clean shadow mode** — no serious errors found in the parallel run

If any of these aren't met, Full Deployment doesn't begin until they are.

---

## 5. Pricing

| Tier | Coverage | Annual price |
|---|---|---|
| Pilot | 50 combinations, validated in shadow mode (Months 1–6) | Same rate as Growth tier from Month 7 — no markup, no hidden discount-then-increase |
| **Growth** | Up to 250 combinations | **€50,000/year** |
| Enterprise | 250+ combinations, multiple markets | €90,000+/year, custom terms |

Plus a one-time onboarding fee (€10,000–25,000, depending on scope) covering source mapping, API integration, and the three workshops in Phase 2.

A self-hosting licence option is available if your data-residency requirements rule out shared infrastructure — ask if this applies to you.

**Source mapping is a shared task:** you provide the list of your target supplier/country combinations and whatever you already know about each document's location; our team handles the technical verification — confirming each source is reachable, classifying its format, and configuring extraction.

**Ongoing review stays with your team:** TermsIQ provides and maintains the review interface and tunes what gets flagged for review, but your content team makes the actual approve/correct decisions on anything flagged. This is by design — your team knows your suppliers, and your team should be the one approving what reaches your customers.

---

## 6. Compliance Position

TermsIQ is classified **Limited Risk** under the EU AI Act (Article 50) — it extracts factual fields for B2B distribution and makes no individualised decisions about your customers. Your business remains responsible for how the data is displayed; TermsIQ's role is to ensure that data is accurate, current, and traceable.

Under GDPR, the core system processes no personal data — only supplier commercial documents. The single external data transfer (LLM extraction) is contractually restricted to EU infrastructure with zero-data-retention terms.

A data processing agreement covering this relationship, including disclosure of any sub-processors used, is provided as part of onboarding.

---

## 7. What We Need From You

| Role | What's needed | When |
|---|---|---|
| **Executive sponsor** (CCO or equivalent) | Sign-off on pilot scope and go/no-go decision at each phase gate | Kickoff; end of Phase 2; Phase 3 go-live |
| **Supplier Partnerships lead** | List of your top 50 supplier/country combinations and known document sources | Phase 2 kickoff |
| **Content/Product Manager** | Co-design the validation workflow; own the ongoing review queue from Phase 3 | Throughout Phase 2; ongoing from Phase 3 |
| **Engineering/CTO** | Confirm the API integration is additive and review the fallback behaviour for low-confidence fields | Before Phase 2 integration begins |
| **Legal/Compliance** | Review the data processing agreement and confidence-threshold policy | Before Phase 2 begins |

---

## 8. Next Step

A 60-day pilot — your top 50 supplier/country combinations, shadow mode first, nothing live until your team has validated the results against real data.

---

*TermsIQ — Deployment Plan*
*Prepared for [Client Name] — June 2026*
