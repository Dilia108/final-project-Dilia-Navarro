# TermsIQ — Use Case Definition
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 2.4 — June 2026

---

## 1. Business Problem Statement

**What problem does TermsIQ solve? For whom?**

Car rental aggregator API providers sit between rental suppliers (Hertz, Avis, Sixt, Europcar, Enterprise, local fleets) and booking channels (OTAs, airline ancillary platforms, metasearch, travel management companies). For every booking they facilitate, a set of supplier terms and conditions governs what the customer is actually agreeing to.

These T&C documents vary by supplier, by pickup country, by driver nationality, and by rate type. They change without notice. They arrive in the most operationally difficult formats possible — PDFs, Excel files, supplier websites in multiple languages, and occasionally phone calls. Almost none of this is delivered via API.

The consequences are documented and severe:
- The European Consumer Centres Network received **6,016 complaints** about car rental companies in 2025, with poor contract transparency consistently highlighted as a primary cause.
- The European Commission found that **55% of screened online car rental intermediaries violate EU consumer law** on T&C transparency.
- Five major suppliers — Hertz, Avis, Europcar, Enterprise, and Sixt — were formally required by the European Commission to improve T&C clarity following regulatory action between 2015 and 2020.

The aggregator sits at the centre of this problem. It receives unstructured T&C documents, attempts to manually normalise them into a content database, and serves what it has — often outdated, incomplete, or absent — to booking channels. When the customer arrives at the rental counter and actual terms differ from what was displayed at booking, the complaint travels upstream to the OTA, and then to the aggregator. **The liability travels upstream.**

**TermsIQ solves this** by using AI to automatically extract structured, machine-readable T&C data from any source format, in any language, and serve it through the aggregator API in real time — with automated change detection when supplier policies update.

The value operates at three levels. First, it reduces the most expensive customer service contacts in the distribution chain — T&C-related disputes (wrong payment card, cancelled booking at counter, unaccepted licence) produce the longest calls, the highest escalation rate, and the most likely churn. Second, it reduces legal and regulatory exposure — the aggregator's liability under EU consumer law is real and active, even if it has not yet materialised as a fine. Third, it creates a commercial differentiator — an aggregator that serves structured, verified, COB-validated T&C data in real time has a genuine and currently unmatched argument with OTA partners.

**Future modelling AI opportunity:**

**Complaint prediction model (v2, requires live data):** A predictive layer identifying which T&C gaps are most likely to generate complaints requires a closed data loop — booking ID, T&C served at time of booking, complaint outcome. This data does not currently exist in one place. TermsIQ creates it from go-live by logging which T&C was served for every booking. If OTA partnerships make complaint outcome data available, the loop closes and a complaint-risk scoring model becomes possible. Target: v2, 12–18 months post go-live.

---

## 2. Company Profile

| Attribute | Detail |
|---|---|
| **Industry** | Travel technology — car rental distribution and API aggregation |
| **Headquarters** | Germany |
| **Company size** | Mid-size travel tech company — 50–300 employees (SME) |
| **Role in value chain** | Sits between rental suppliers and booking channels (OTAs, airlines, TMCs) |
| **Supplier coverage** | 100–500 rental suppliers across 50+ countries |
| **Current T&C state** | Manual process: content team maintains a spreadsheet of supplier terms, updated reactively when complaints are received or when a supplier notifies of a change. Critical fields — especially grace period and payment acceptance — are either absent from the API response or incorrect for a material percentage of supplier/country combinations. |
| **Data sources currently used** | PDF documents from suppliers, Excel files, supplier websites (manual review), phone/email from supplier account managers |
| **Key pain points** | Legal and commercial exposure from T&C inaccuracies; OTA partners losing trust due to counter disputes; content team spending disproportionate time on manual maintenance instead of commercial work |
| **Operational maturity** | Established, revenue-generating business with existing API infrastructure. No AI capabilities in production. Manual content processes are a known bottleneck. |
| **Data residency requirement** | All data must be stored and processed within Germany, in compliance with GDPR and internal data governance policy. |

---

## 3. Proposed AI Solution

### What TermsIQ does

TermsIQ is an AI-powered document intelligence pipeline that automatically extracts structured, machine-readable T&C data from unstructured supplier sources — PDFs, Excel files, and web pages in any language — and serves it through the aggregator's existing API infrastructure in real time.

### Type of AI system

| Dimension | Detail |
|---|---|
| **Primary AI type — v1** | Generative AI / Large Language Model (extraction and structured output generation) |
| **Primary AI type — v2** | Predictive Modelling (complaint risk scoring per booking — requires closed data loop) |
| **Secondary functions** | Classification (confidence scoring, document change detection), Automation (pipeline orchestration, monitoring) |
| **Model architecture — v1** | Dual-provider: OpenAI GPT-4o (primary) + Anthropic Claude Sonnet (fallback) — see routing logic below |
| **Infrastructure** | All infrastructure hosted in Germany to meet data residency requirements |

### AI maturity roadmap

TermsIQ is designed as a three-phase AI system. Each phase builds directly on the previous one.

| Phase | Version | When | What | Why |
|---|---|---|---|---|
| **Prompt engineering** | v1 | Now | General-purpose GPT-4o with per-supplier few-shot examples embedded in the prompt; prompts continuously refined based on human review corrections | Available immediately; no training data required; few-shot examples handle known terminology variants; human corrections feed directly back into prompt improvement |
| **Complaint prediction** | v2 | 12–18 months post go-live | Train a complaint-risk scoring model on booking ID → T&C served → complaint outcome data | Requires live data accumulation; TermsIQ generates this dataset from day one by logging T&C served per booking |

**Why prompt engineering with few-shot examples is the right approach for v1:** the annotation work already done (Hertz ES/DE, Sixt ES/DE, Goldcar ES across all five fields) provides exactly the few-shot examples needed. Each annotated source text + extracted value pair is embedded directly in the prompt, teaching the model the supplier-specific terminology patterns without any training infrastructure. This is faster to build, easier to update, and produces results that are measurable against the ground truth immediately.

### Model routing logic

TermsIQ uses a dual-provider LLM architecture to avoid vendor lock-in, maximise resilience, and optimise cost and accuracy by task type.

| Scenario | Model used | Reason |
|---|---|---|
| Standard extraction (well-structured PDF, clear language) | OpenAI GPT-4o (primary) | Strong structured output performance, wide language support |
| Ambiguous, poorly-structured, or low-confidence documents | Anthropic Claude Sonnet (fallback) | Strong reasoning on complex or contradictory language |
| Primary provider unavailable or rate-limited | Automatic failover to the other provider | Operational resilience — no single point of failure |
| Confidence score below threshold on first pass | Re-run on secondary provider; human review if still low | Quality safeguard before any data goes live |

Both providers must be evaluated for EU data residency compliance before go-live. OpenAI offers EU data residency via Azure OpenAI Service (Germany North region). Anthropic data processing terms must be reviewed and confirmed with legal before production use.

### The five-stage pipeline

**Stage 1 — Ingest:** Accept any document format from any supplier source. PDFs uploaded directly, Excel files via SFTP drop, web pages via scheduled crawl. OCR applied to scanned documents.

**Stage 2 — Extract:** The LLM reads each document and extracts the five critical fields — TPL amount, grace period, licence acceptance rules, payment acceptance rules, and cross-border conditions — per country where those rules apply. Output is structured JSON conforming to a defined schema.

**Stage 3 — Validate:** Extracted data is checked against a validation schema. Values outside expected ranges trigger a human review flag. Confidence scores are attached to each extracted field.

**Stage 4 — Store & version:** Validated data is written to the T&C knowledge base, hosted in Germany, keyed by supplier × pickup country × rule type. All previous versions are retained. Every change is timestamped and attributed to the source document.

**Stage 5 — Serve & monitor:** T&C data is served via the aggregator's existing API response — new fields appended to the standard car availability response. A change-detection monitor runs daily. When a supplier document changes, the diff is extracted, reviewed, and the knowledge base updated. Stakeholders are alerted automatically.

### Supplier scope — v1

TermsIQ v1 covers the following 10 suppliers. Global majors are scoped across all operational markets. Regional specialists are scoped to their home markets only in v1.

| Supplier | Type | v1 Market scope |
|---|---|---|
| **Hertz** | Global major | All operational markets |
| **Sixt** | Global major | All operational markets |
| **Avis / Budget** | Global major | All operational markets |
| **Europcar** | Global major | All operational markets |
| **Enterprise / National / Alamo** | Global major | All operational markets |
| **Centauro** | Regional specialist | Spain (home market) |
| **Goldcar** | Regional specialist | Spain (home market) |
| **Sicily by Car** | Regional specialist | Italy (home market) |
| **Noleggiare** | Regional specialist | Italy (home market) |
| **Hertz Avaza** | Regional specialist | Mexico (home market) |

All remaining suppliers in the aggregator's network are out of scope for v1 and will be prioritised for v2 based on booking volume and complaint rate.

### COB cross-check for TPL resolution

For European markets, the TPL extraction logic includes a mandatory cross-check against the **Council of Bureaux (COB) Minimum Amount of Coverage reference document** (edition April 2026, sourced from cobx.org). This is required because most supplier T&C documents do not state an explicit TPL amount — they reference "statutory minimum" or omit TPL entirely, which is legally correct but operationally insufficient for the distribution chain.

**The cross-check logic:**

| What the supplier document says | TermsIQ action |
|---|---|
| States an explicit TPL amount | Use supplier figure; label source as "supplier T&C" |
| References statutory minimum | Query COB 2026 table for pickup country; return statutory amount labelled as "COB 2026 statutory minimum" |
| Silent on TPL | Same as above — COB lookup triggered automatically |
| COB data is stale (>18 months) | Return COB figure with staleness flag and `recommend_verification = true` |
| COB value is "unlimited" | Return `tpl_display = "unlimited"` with note; confidence = HIGH |
| No COB data available (e.g. Austria) | Return `tpl_display = "not_available"`; flag for manual verification; include COB source URL |

**Key statutory amounts from COB 2026 for priority markets:**

| Country | Personal injury (per accident) | Property damage (per accident) | COB data date |
|---|---|---|---|
| Germany | €7,500,000 | €1,300,000 | Dec-25 |
| Spain | €70,000,000 | €15,000,000 | Dec-25 |
| Italy | €6,450,000 | €1,300,000 | Dec-25 |
| United Kingdom | £1,200,000 | £1,200,000 | Dec-25 |
| Norway | Unlimited | €8,484,643 | Dec-25 |
| Switzerland | CHF 5,000,000 per claim | — | Nov-24 |
| Austria | ⚠️ No data — manual verification required | — | Oct-21 |

**Important:** The COB document carries an explicit disclaimer that figures are provided for information only and COB assumes no responsibility for accuracy or future changes. All COB-sourced figures in the API response must be labelled with their source and data date, and must not be presented as legally guaranteed amounts.

TermsIQ monitors the COB document URL monthly for new editions and updates the knowledge base automatically when a new edition is published.

### Output language

| Language | Role | Delivery |
|---|---|---|
| **English** | Primary output language | All API responses, extracted field values, confidence metadata, and fallback messages |
| **German** | Secondary output language | All API responses served to German-market OTA partners; field labels, status messages, and fallback text localised to German |

Source documents are ingested and processed in any language (German, Spanish, Italian, English, French, and others). The extraction output is always delivered in English and German regardless of the source document language.

### The five critical T&C fields (Minimum Viable Scope)

#### 1. Third Party Liability (TPL) amount
TPL varies by country law, by supplier, and sometimes by vehicle category. EU member states each have different statutory minimum TPL amounts — Spain's minimum (€70,000,000 personal injury) is nearly eleven times the EU MID floor of €6.45M. Most supplier T&C documents reference "statutory minimum" rather than stating a number — because the law determines it, not the supplier. This is legally correct but operationally insufficient for the distribution chain.

When the customer's displayed coverage differs from the actual policy at pickup, the OTA that showed the incorrect figure faces potential consumer law liability under EU Directive 93/13/EEC on Unfair Contract Terms. TermsIQ resolves this through a three-layer logic:
1. Extract if the supplier states an explicit amount.
2. If the supplier references statutory minimum, query the Council of Bureaux (COB) reference database for the pickup country statutory amount.
3. If no COB data is available, return a flagged "requires verification" response with the COB source link.

This turns a data absence into an intelligent resolution — which is exactly what AI adds that a rule-based system cannot.

#### 2. Grace period for vehicle pickup
Almost entirely absent from aggregator API responses. Supplier policies range from 29 minutes to 2+ hours (Goldcar holds bookings for 6 hours), with some suppliers auto-cancelling with no refund at the scheduled time. For airport pickups involving delayed flights, this is the most operationally urgent piece of information a customer needs. Currently managed by outdated content team notes and supplier phone calls. No systematic, reliable, real-time source exists anywhere in the distribution chain.

#### 3. Licence type accepted
Three intersecting dimensions make this complex: the customer's licence-issuing country, the pickup country, and the supplier's own policy. Hertz structures their T&C into global rental terms and country-specific terms — with country-specific terms explicitly taking precedence. Sixt Germany explicitly states that photocopies and digital licences will not be accepted, and that foreign licences not in German require a certified translation unless an EU/EEA exemption applies. An Australian licence in Spain is accepted by some suppliers and rejected by others. No aggregator API currently handles all three dimensions dynamically. Source countries of primary concern: **Germany, Switzerland, Spain**.

#### 4. Payment type accepted
Credit card versus debit card is the single biggest source of counter disputes in car rental globally. Most major suppliers require a credit card for the security deposit — but exceptions exist per supplier, per rate type (prepaid vs pay-at-counter), and per pickup country. A customer who arrives at the counter with a debit card for a prepaid reservation, believing their payment was already settled, may find their booking refused with no recourse. This scenario is almost never accurately represented in the aggregator API. Goldcar, for example, accepts only Visa and Mastercard — a significantly narrower acceptance policy than Sixt or Hertz, which is not surfaced anywhere in the current distribution chain.

#### 5. Cross-border conditions *(newly added)*
Many suppliers impose specific restrictions or requirements when the rented vehicle is taken across national borders. These conditions vary significantly by supplier and pickup country — and violations invalidate all insurance coverage. Sixt uses a four-zone system covering 25+ European countries with category-specific restrictions. Goldcar limits permitted countries to just five (Andorra, France, Italy, Portugal, Gibraltar) plus specific island rules — enforced via GPS tracking with automatic contract termination on violation. Hertz uses a map-based system with country-specific forbidden lists. Currently completely absent from most aggregator API responses. This field is critical for markets where cross-border rental is common, including Germany, Switzerland, and Spain.

### Operational markets

| Region | Countries |
|---|---|
| **Central Europe** | Germany, Switzerland |
| **Southern Europe** | Spain, Italy |
| **Western Europe** | United Kingdom, Norway |
| **North America** | United States, Canada |
| **Latin America** | Mexico, Costa Rica, Panama |

**Driver source countries (primary):** Germany, Switzerland, Spain — these determine the licence type logic and cross-border condition priority.

---

## 4. Key Stakeholders

| Stakeholder | Role | Interest in TermsIQ |
|---|---|---|
| **Chief Commercial Officer** | Primary sponsor — owns OTA partnership relationships | Every counter dispute damages OTA relationships. Needs TermsIQ to remove the aggregator as the weak link in T&C quality. |
| **Head of Supplier Partnerships** | Manages rental supplier relationships | Currently acts as informal T&C communication channel. TermsIQ transforms this role from manual data entry to exception management and supplier engagement. |
| **Content / Product Manager** | Owns current manual T&C process | Most directly affected. Daily workload changes from PDF reading to exception management and data governance. Must be co-designer of the validation workflow. Critical change management stakeholder. |
| **Head of Engineering / CTO** | Technical decision-maker | Evaluates integration complexity, latency, and fallback behaviour. T&C data is cached — not computed per request. Must be satisfied that TermsIQ appends new fields without breaking existing API contracts. |
| **Compliance Officer** | Gatekeeper — data protection | EU AI Act classification, GDPR data flow, legal basis for web crawling. Must be involved before any web crawling is built and before T&C data is served live. |
| **Legal** | Risk reviewer | Liability for incorrect extractions, web scraping legality, IP position on supplier T&C documents. Must review before supplier web crawling goes live and before OTA contracts reference TermsIQ data fields. |
| **OTA / Channel partners** | Indirect stakeholder — downstream beneficiary | Currently absorb complaints and chargebacks from T&C inaccuracies. Will benefit directly from improved data quality. Potential advocates if their counter dispute rate drops measurably. |

---

## 5. Success Criteria

| # | Metric | Target | Measurement method |
|---|---|---|---|
| 1 | **T&C field coverage** | ≥90% of active supplier/country combinations have all 5 critical fields extracted and served via API within 90 days of go-live | API response audit across active supplier/country matrix |
| 2 | **Extraction accuracy** | ≥95% accuracy on the 5 critical fields, validated against manually verified ground truth | Blind validation set reviewed by content team |
| 3 | **Change detection speed** | Supplier T&C updates reflected in the knowledge base within 24 hours of document change | Timestamped log of source document change vs knowledge base update |
| 4 | **Content team time saving** | ≥60% reduction in manual T&C maintenance hours per month within 90 days | Monthly hours log before and after go-live |
| 5 | **Counter dispute reduction** | Measurable reduction in T&C-related counter disputes reported by OTA partners within 6 months | OTA partner dispute logs, tagged by dispute type |
| 6 | **API latency** | T&C fields served with ≤50ms additional latency on the existing search response | API performance monitoring |
| 7 | **Confidence coverage** | <5% of API responses return "data not available" fallback after 90 days | API response metadata audit |
| 8 | **Cross-border field coverage** | Cross-border conditions extracted and served for all top 20 supplier/pickup country combinations involving Germany, Switzerland, and Spain within 90 days | API response field audit |

---

## 6. Out-of-Scope Boundaries

TermsIQ v1 explicitly will **not** do the following:

| Out-of-scope item | Reason / future phase |
|---|---|
| **Additional T&C fields** beyond the 5 critical ones (e.g. vehicle excess amounts, age restrictions, young driver surcharges) | High value but deferred to v2 to maintain delivery focus. Exception: cross-border conditions are in scope for v1. |
| **Fuel policy** | Fuel policy is operational/vehicle data — not a T&C field. It is encoded in the SIPP code and served directly via the supplier API alongside availability and pricing. TermsIQ does not touch this data layer. |
| **Customer-facing display of T&C** | A different product with a different buyer. TermsIQ is an aggregator-layer API product — it does not interact directly with end consumers or OTA booking interfaces. |
| **Legal interpretation of extracted T&C content** | TermsIQ extracts and structures factual content. It does not provide legal advice, assess regulatory compliance on behalf of clients, or interpret ambiguous legal language. Human review and legal sign-off remain required for edge cases. |
| **Supplier contract negotiation or T&C modification** | TermsIQ reads and extracts what suppliers publish. It does not negotiate, amend, or influence supplier T&C content. |
| **Custom training or fine-tuning of AI models** | TermsIQ v1 uses OpenAI and Anthropic APIs via prompt engineering and per-supplier few-shot examples. No custom model training is in scope for v1. The annotation work already completed (Hertz, Sixt, Goldcar across ES and DE) serves directly as few-shot examples embedded in the extraction prompt — not as fine-tuning training data. |
| **Real-time webhook alerts to OTA partners** | Push notifications to OTA partners when T&C changes would require OTA API integration. Deferred to v2. |
| **Supplier self-service upload portal** | A web interface for suppliers to upload their own T&C documents directly. Deferred to v2. |
| **Processing of personal data** | TermsIQ processes only supplier commercial documents — not customer or driver personal data. Any pipeline extension that would process personal data requires a separate GDPR assessment before build. |
| **Data storage or processing outside Germany** | All infrastructure, data storage, and AI API processing must remain within Germany. Any model or infrastructure option — including LLM API providers — that cannot guarantee German data residency is out of scope. |
| **Markets outside the defined operational scope** | v1 covers Germany, Switzerland, Spain, Italy, United Kingdom, Norway, United States/Canada, and Latin America (Mexico, Costa Rica, Panama). Additional markets require a scope extension decision. |

---

*TermsIQ — Use Case Definition*
*Document version 2.5 — June 2026*
*Incorporates: German data residency, operational market scope, cross-border conditions, full structured use case framework, named supplier list (10 suppliers), COB 2026 TPL cross-check, English/German output language, dual-provider LLM architecture, fuel policy clarification (SIPP code), ECRCS 2025 field validation, two-phase AI maturity roadmap (prompt engineering → complaint prediction), multi-document architecture note, terminology normalisation via few-shot examples (not fine-tuning), field descriptions strengthened with supplier-specific evidence from live POC testing (Hertz ES/DE, Sixt ES, Goldcar ES)*
