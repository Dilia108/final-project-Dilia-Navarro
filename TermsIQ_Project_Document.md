# TermsIQ
## Intelligent Terms & Conditions Extraction for Car Rental Distribution

**Project document — Use Case Definition & Market Feasibility Research**
Prepared for: [Client name]
Date: June 2026
Version: 1.0

---

## Section 1 — Use Case Definition

### 1.1 Business problem

Car rental aggregator API providers connect hundreds of rental suppliers to thousands of booking channels worldwide. For every booking they facilitate, a set of supplier terms and conditions governs what the customer is actually agreeing to — covering critical fields such as third party liability coverage, grace period for vehicle pickup, accepted licence types, and accepted payment methods.

These terms vary by supplier, by pickup country, by driver nationality, and by rate type. They change without notice. And they arrive from suppliers in the most operationally difficult formats possible: PDF documents, Excel spreadsheets, supplier websites in multiple languages, and occasionally phone calls. Almost none of this is delivered via API.

The consequences are severe and documented. The European Consumer Centres Network received **6,016 complaints** about car rental companies in 2025 alone, with poor contract transparency consistently highlighted as a primary cause. The European Commission found that **55% of screened online car rental intermediaries violate EU consumer law** on T&C transparency. Five major suppliers — Hertz, Avis, Europcar, Enterprise and Sixt — were formally required by the European Commission to improve T&C clarity following regulatory action between 2015 and 2020.

The aggregator sits at the centre of this problem. It receives unstructured T&C documents from suppliers, attempts to manually normalise them into a content database, and serves what it has — which is often outdated, incomplete, or simply absent — to the booking channels that depend on it. The booking channel then displays whatever it receives (or nothing) to the customer.

When the customer arrives at the rental counter and the actual terms differ from what was displayed at booking — the wrong payment card, an unacceptable licence, a cancelled booking because the grace period was not shown — the complaint lands on the OTA, which traces back to the aggregator. The liability travels upstream.

**TermsIQ solves this by using AI to automatically extract structured, machine-readable T&C data from any source format, in any language, and serve it through the aggregator API in real time — with automated change detection when supplier policies update.**

---

### 1.2 The five critical T&C fields

These are the fields that cause the most real-world friction at the rental counter and the most complaints in the distribution chain. Four of them — TPL, grace period, licence type, and payment — are the core v1 scope. Cross-border conditions are included as a v1 bonus field: the annotation work and pipeline already support it, and it addresses a documented source of counter disputes. It is presented separately in the API response to reflect its higher complexity and the fact that confidence scores are more variable across suppliers.

#### Third party liability (TPL) amount

TPL varies by country law, by supplier, and sometimes by vehicle category. EU member states each have different statutory minimum TPL amounts. Most aggregator APIs return either nothing, a generic flag, or a figure that was manually entered months ago. When the customer's displayed coverage differs from the actual policy at pickup, the OTA that showed the incorrect figure faces potential consumer law liability under EU Directive 93/13/EEC on Unfair Contract Terms.

#### Grace period for vehicle pickup

Almost entirely absent from aggregator API responses. Supplier policies range from 29 minutes to 2+ hours, with some suppliers auto-cancelling with no refund at the scheduled time. For airport pickups involving delayed flights, this is the most operationally urgent piece of information a customer needs. Currently managed by outdated content team notes and supplier phone calls. No systematic, reliable, real-time source exists anywhere in the distribution chain.

#### Licence type accepted

Three intersecting dimensions make this exceptionally complex: the customer's licence-issuing country, the pickup country, and the supplier's own policy. Hertz structures their T&C into global rental terms and country-specific terms — with country-specific terms explicitly taking precedence. Sixt Germany states explicitly that photocopies and digital licences will not be accepted, and that foreign licences not in German require a certified translation unless an EU/EEA exemption applies. An Australian licence in Spain is accepted by some suppliers and rejected by others. No aggregator API currently handles all three dimensions dynamically.

#### Cross-border conditions (v1 bonus field)

Cross-border rules vary significantly by supplier, vehicle category, and pickup country, and violations invalidate all insurance coverage. Sixt uses a four-zone system covering 25+ European countries with category-specific restrictions. Goldcar limits permitted countries to just five (Andorra, France, Italy, Portugal, Gibraltar) plus specific island rules — enforced via GPS tracking. Hertz uses a map-based system with country-specific forbidden lists. This field is more complex than the core four — permitted country lists are long, and confidence scores are more variable — which is why it is presented as a v1 bonus field rather than a core claim. The pipeline already extracts it from the same document in the same API call.

#### Payment type accepted

Credit card versus debit card is the single biggest source of counter disputes in car rental globally. Most major suppliers require a credit card for the security deposit — but exceptions exist per supplier, per rate type (prepaid vs pay-at-counter), and per pickup country. A customer who arrives at the counter with a debit card for a prepaid reservation, believing their payment was already settled, may find their booking refused with no recourse. This scenario is almost never accurately represented in the aggregator API.

---

### 1.3 Company profile

| Attribute | Detail |
|---|---|
| Industry | Travel technology — car rental distribution and API aggregation |
| Role in value chain | Sits between rental suppliers (Hertz, Avis, Enterprise, Sixt, Europcar, local fleets) and booking channels (OTAs, airline ancillary platforms, metasearch, travel management companies) |
| Size | Mid-size travel tech company — 50–300 employees, managing supplier connectivity for 100–500 rental suppliers across 50+ countries |
| Current T&C state | Manual process: content team maintains a spreadsheet of supplier terms, updated reactively when complaints are received or when a supplier notifies of a change. Significant fields — especially grace period and payment acceptance — are either absent from the API response or incorrect for a material percentage of supplier/country combinations |
| Data sources currently used | PDF documents from suppliers, Excel files, supplier websites (manual review), phone/email from supplier account managers |
| Key pain | Legal and commercial exposure from T&C inaccuracies; OTA partners losing trust due to counter disputes; content team spending disproportionate time on manual T&C maintenance instead of commercial work |

---

### 1.4 Proposed AI solution — TermsIQ

TermsIQ is an AI-powered document intelligence pipeline that automatically extracts structured, machine-readable T&C data from unstructured supplier sources — PDFs, Excel files, and web pages in any language — and serves it through the aggregator's existing API infrastructure in real time.

**The pipeline has five stages:**

**Stage 1 — Ingest:** Accept any document format from any supplier source. PDFs uploaded directly, Excel files via SFTP drop, web pages via scheduled crawl. OCR applied to scanned documents.

**Stage 2 — Extract:** A large language model (Claude Sonnet via the Anthropic API) reads each document and extracts five T&C fields — TPL amount, grace period, licence acceptance rules, payment acceptance rules, and cross-border conditions — per country where those rules apply. Output is structured JSON conforming to a defined schema. The four core fields (TPL, grace period, licence, payment) are the primary v1 deliverable; cross-border conditions are extracted in the same call and served as a bonus field with its own confidence score.

**Stage 3 — Validate:** Extracted data is checked against a validation schema. Values outside expected ranges (e.g. a TPL of €0 or a grace period of 500 minutes) trigger a human review flag. Confidence scores are attached to each extracted field.

**Stage 4 — Store & version:** Validated data is written to the T&C knowledge base, keyed by supplier × pickup country × rule type. All previous versions are retained. Every change is timestamped and attributed to the source document.

**Stage 5 — Serve & monitor:** T&C data is served via the aggregator's existing API response — new fields appended to the standard car availability response. A change-detection monitor runs daily: when a supplier document changes, the diff is extracted, reviewed, and the knowledge base is updated. Stakeholders are alerted automatically.

**What TermsIQ does not do:** it does not replace the human judgement required for complex edge cases or legal interpretation. It eliminates the manual extraction work and ensures that the human reviewer is looking at a structured diff of what changed — not reading a 40-page PDF from scratch.

---

### 1.5 Key stakeholders

#### Chief Commercial Officer — Primary sponsor
Owns the OTA partnership relationships. Every counter dispute that traces back to incorrect T&C information damages those relationships. Needs a solution that removes the aggregator as the weak link in T&C quality.

#### Head of Supplier Partnerships
Manages the relationship with rental suppliers. Currently acts as the informal T&C communication channel — chasing suppliers for updates, translating policy changes from supplier emails into the content database. TermsIQ transforms this role from manual data entry to exception management and supplier engagement.

#### Content / Product Manager
Owns the current manual T&C maintenance process. The person most directly affected by TermsIQ — their daily workload changes fundamentally. Must be involved as a co-designer of the validation workflow and exception handling process. Critical change management stakeholder.

#### Head of Engineering / CTO
Evaluates integration complexity. TermsIQ appends new fields to the existing API response — it does not replace the API. Must be satisfied with the latency profile (T&C data is cached, not computed per request), the confidence score mechanism, and the fallback behaviour when data is absent.

#### OTA / Channel partners — Indirect stakeholder
The downstream customers who display T&C to end consumers. Currently deal with complaints and chargebacks from T&C inaccuracies. Will benefit directly from improved data quality. May become advocates for TermsIQ if their complaint rate drops measurably.

#### Compliance Officer — Gatekeeper
The EU consumer law context (55% of intermediaries in violation, ongoing EC monitoring) makes this a compliance project, not just a product project. Must review the T&C data pipeline for GDPR compliance and assess whether automated extraction from supplier documents requires any specific legal basis.

#### Legal — Risk reviewer
Reviews liability implications of serving AI-extracted T&C data. If TermsIQ extracts an incorrect grace period and a customer loses a booking as a result, what is the aggregator's liability position? Legal must define the confidence threshold below which the API response falls back to "terms not available" rather than serving a potentially incorrect value.

---

### 1.6 Success criteria — what does "this works" look like?

| Metric | Target |
|---|---|
| T&C field coverage | 4 core fields extracted and served via API for ≥90% of active supplier/country combinations within 90 days; cross-border conditions served as bonus field for ≥75% of combinations |
| Extraction accuracy | ≥95% accuracy on the four critical fields, validated against manually verified ground truth |
| Change detection speed | Supplier T&C updates reflected in the knowledge base within 24 hours of document change |
| Content team time saving | ≥60% reduction in manual T&C maintenance hours per month |
| Counter dispute rate | Measurable reduction in T&C-related counter disputes reported by OTA partners within 6 months |
| API availability | T&C fields served with ≤50ms additional latency on the existing search response |
| Confidence coverage | <5% of API responses return "data not available" fallback after 90 days |

---

## Section 2 — Market & Feasibility Research

### 2.1 Jobs-to-be-done (JTBD)

**User persona:** Head of Supplier Partnerships / Content Manager at a car rental aggregator API provider.

| Dimension | Statement |
|---|---|
| **Functional** | Automatically extract, maintain, and serve accurate terms and conditions for every supplier and pickup country combination — without manually reading PDFs, chasing supplier account managers, or maintaining a spreadsheet that is always slightly out of date. |
| **Emotional** | Feel confident that the T&C data in the API is accurate and current — not anxious every time an OTA reports a counter dispute that traces back to something the content team missed six months ago. |
| **Social** | Be seen by OTA partners and regulatory bodies as the most reliable, transparent aggregator in the market — one that takes T&C accuracy seriously rather than treating it as a content maintenance afterthought. |

---

### 2.2 MoSCoW prioritisation

| Feature | Category | Rationale |
|---|---|---|
| PDF/document ingestion pipeline | Must have | No extraction is possible without reliable document parsing. Foundation of the system. |
| LLM extraction for the 4 critical fields | Must have | The core AI capability. TPL, grace period, licence type, payment type — these four fields address the most documented consumer pain points. |
| Structured JSON output per supplier × country | Must have | The API integration requires machine-readable output in a defined schema. Without this, the data cannot be served downstream. |
| Confidence score per extracted field | Must have | Legal and compliance requirement. Low-confidence extractions must not be served as facts. The fallback to "data not available" protects the aggregator from liability for incorrect data. |
| Human review queue for low-confidence extractions | Must have | AI accuracy is not 100%. A review interface for flagged fields is required before any data goes live in the API. |
| Change detection and alerting | Should have | T&C documents change without notice. Automated monitoring is essential for maintaining accuracy after initial extraction — but can be manual weekly checks at MVP. |
| Multi-language extraction (non-English PDFs) | Should have | A significant proportion of supplier documents are in Spanish, German, French, Italian. LLM extraction handles this natively — but requires validation across languages. |
| Excel and web page ingestion | Should have | Many suppliers send Excel files; some publish terms only on their website. MVP can focus on PDF; other formats follow in growth phase. |
| Version history and audit trail | Should have | Compliance requirement — the aggregator must be able to show what T&C was served at any point in time for any booking. |
| API field extension (serve via existing response) | Should have | The distribution mechanism. Can be served as supplementary fields without breaking existing API contracts. |
| Supplier self-service portal | Could have | A web interface where supplier account managers can upload new T&C documents directly. Reduces dependency on content team as intermediary. |
| Cross-border conditions | Should have | Extracted in the same pipeline call as the four core fields — no additional effort. Higher confidence variability than core fields (supplier zone systems are complex) makes it a v1 bonus field rather than a core claim, but the annotation work is already done and the extraction is live. |
| Additional T&C fields (fuel policy, excess amounts) | Could have | High value but out of scope for v1. The five fields are the minimum viable product. |
| Real-time webhook alerts to OTA partners | Could have | Push notifications to OTA partners when a supplier's T&C changes. Valuable but requires OTA API integration work. |
| Automatic T&C display on booking confirmation | Won't have | Customer-facing feature — a different product with a different buyer. Out of scope for the aggregator API layer. |

---

### 2.3 RICE scoring — two key features compared

**Formula:** RICE score = (Reach × Impact × Confidence) ÷ Effort

| Feature | Reach | Impact | Confidence | Effort | RICE Score | Verdict |
|---|---|---|---|---|---|---|
| LLM extraction of 5 T&C fields | 500 supplier/country combinations | 3.0 (massive — direct compliance and legal risk reduction) | 0.85 | 2 person-months | **637,500** | Build first |
| Change detection and alerting | 500 supplier/country combinations | 2.0 (high — accuracy degrades over time without this) | 0.80 | 1 person-month | **800,000** | Build second |

**Analysis:** Change detection scores higher than the core extraction on a pure RICE basis because the effort is lower and the confidence is high — it is a well-understood engineering problem. However, it has a hard dependency on the extraction being live first. The correct build order is extraction → change detection, even though the RICE score inverts them. This is an important observation: RICE scores features in isolation, not in dependency order. Always cross-check with the dependency map.

---

### 2.4 Validation framework

| Validation type | Confidence | Evidence |
|---|---|---|
| **Market** | High | ECC-Net received 6,016 car rental complaints in 2025 (ECC-Net, 2025). European Commission found 55% of screened car rental intermediaries violate EU consumer law on T&C transparency (EC, 2022). Five major suppliers were formally required to improve T&C clarity by EU regulators (CPC Network, 2017–2020). Car rental is consistently one of the top areas of consumer rights complaints in the EU. The regulatory pressure is active, not historical. |
| **User** | High | This is a pain point directly validated by the project author through years of direct professional experience at a car rental aggregator. The manual T&C maintenance process — PDFs, Excel files, supplier phone calls — is not a hypothesis. It is the current operational reality at aggregators across the industry. Recommended next step: 2–3 validation interviews with content managers or supplier relations staff at other aggregators to confirm scope and willingness to pay. |
| **Competitive** | High | No existing aggregator API provider serves structured, AI-extracted T&C data across all four critical fields in real time. Content management tools exist (e.g. Stibo Systems, Akeneo) but are generic and not car rental-specific. The closest analogues are legal tech document extraction tools (Kira, Luminance) built for contracts — not for car rental T&C in a distribution API context. This gap is the commercial opportunity. |
| **Feasibility** | High | LLM-based document extraction is proven technology as of 2025–2026. The Anthropic Claude API handles PDF ingestion natively. Hertz publishes country-specific T&C PDFs at publicly accessible URLs (e.g. images.hertz.com/pdfs/RT_FULL_ES_EN.pdf, RT_FULL_DE_EN.pdf). Sixt publishes rental information per country on their website. Demo data is downloadable today. Full MVP stack is buildable with Python + LangChain/Anthropic SDK + FastAPI + PostgreSQL — all open source or free tier. |

---

### 2.5 Market evidence — what is real vs hype

#### Evidenced statistics

| Statistic | Source | Context |
|---|---|---|
| 6,016 complaints in 2025 | ECC-Net, 2025 | Car rental complaints to European Consumer Centres — up sharply. T&C transparency and hidden fees are leading causes. |
| 55% violate EU law | European Commission, 2022 | Of screened online car rental intermediaries found to violate EU consumer law — primarily T&C transparency failures. |
| 5 suppliers formally required to act | CPC Network / EC, 2017–2020 | Hertz, Avis, Europcar, Enterprise, Sixt all committed to T&C improvements under regulatory pressure. Compliance was uneven and required ongoing monitoring. |
| LLMs transform unstructured to structured data | McKinsey, 2024–2025 | Documented across industries — AI extraction of structured data from unstructured documents is one of the highest-ROI AI applications in enterprise settings. |
| 4–8 weeks per aggregator integration | Acquaint Softtech, 2026 | Industry estimate for OTA content normalisation per aggregator — confirming that manual content work at this scale is expensive and persistent. |

#### What is real and evidenced

- T&C transparency is a documented, actively-enforced EU regulatory problem in car rental
- The four critical fields (TPL, grace period, licence type, payment type) are under-served or absent in aggregator APIs today — confirmed by industry professionals and consumer complaint data
- LLM-based extraction from PDFs is proven technology available via commercial APIs today
- Supplier T&C documents are publicly available for major suppliers — Hertz, Sixt, Avis, Europcar all publish country-specific terms online
- The problem is operationally confirmed — content teams at aggregators spend significant manual effort on T&C maintenance that TermsIQ replaces

#### What is hype or requires caution

- LLM extraction accuracy is not 100% — for legal documents, a human review step for low-confidence extractions is non-negotiable
- "Real-time" extraction from every supplier for every country is not realistic at v1 — the value is in automating what is currently manual, not in achieving instantaneous universal coverage
- LLMs can hallucinate. A TPL amount that was confidently extracted but is incorrect is more dangerous than a missing field. The confidence score and human review queue are safety-critical, not optional
- The technology is available but the data cleaning work is significant — supplier PDFs use inconsistent terminology, inconsistent structure, and occasionally contradict their own content

#### The honest TermsIQ benchmark

The credible v1 target is: 90% field coverage for the four critical fields across the top 50 supplier/country combinations, with ≥95% extraction accuracy on validated ground truth. This eliminates the majority of T&C-related counter disputes and removes the content team from the critical path for routine maintenance — freeing them for supplier relationship work that creates commercial value.

---

## Section 3 — Stakeholders, Legal & Compliance

### 3.1 Compliance stakeholder

**Stakeholder:** Data Protection / Compliance Officer

**What they want to know before launch:**

- Does TermsIQ process any personal data? (It processes supplier documents — not customer data — so GDPR risk is low, but the data flow must be documented.)
- What is the legal basis for crawling supplier websites to extract T&C content? (Supplier T&C documents are public-facing — but the terms of use of supplier websites may restrict automated access. Legal review required before any web crawling goes live.)
- Can the aggregator demonstrate, for any booking, what T&C was served at the time of search? (Audit trail and version history are required for EU consumer law compliance.)
- Is the confidence score threshold documented, and is there a formal process for what happens below it? (The decision to serve "data not available" vs serving a low-confidence extraction must be a documented policy, not an ad hoc judgement.)

**Earliest involvement point:** Before the web crawling component is built and before any T&C data is served live to channel partners.

**Mitigation already in design:** TermsIQ processes only supplier commercial documents — no personal data from customers or drivers. Version history and audit trail are built into the pipeline architecture. Confidence scores are attached to every extracted field, and the human review queue is a mandatory step before any field goes live.

---

### 3.2 Legal stakeholder

**Stakeholder:** General Counsel / Legal team

**What they want to know before launch:**

- **Liability for incorrect extractions:** If TermsIQ extracts an incorrect grace period and a customer loses a booking as a result, what is the aggregator's liability? Legal must define the confidence threshold and the contractual language with OTA partners that clarifies the aggregator's data accuracy obligations.
- **Web scraping legality:** Crawling supplier websites to extract T&C content may conflict with supplier website terms of use. The safer approach — requesting T&C documents directly from suppliers via the existing account manager relationship — should be the default, with web crawling as a fallback only after legal review.
- **EU AI Act classification:** TermsIQ processes legal documents and outputs structured data that affects what consumers are shown at booking. This may fall within the EU AI Act's transparency requirements for automated systems — requires classification review.
- **Intellectual property:** Supplier T&C documents are copyrighted. Extracting structured data fields from them (as opposed to reproducing the text) is generally acceptable under EU law, but the legal boundary requires explicit review.

**Earliest involvement point:** Before any supplier web crawling, before OTA partner contracts are updated to reference TermsIQ data fields, and before the system goes live in any EU market.

> **The common mistake:** assuming that because T&C documents are publicly available, processing them automatically is legally unrestricted. Public availability does not equal permission for automated commercial use. Legal must confirm the data sourcing approach before engineering builds it.

---

## Section 4 — Cost Estimation & Go-to-Market

### 4.1 Complete cost model

TermsIQ uses the Anthropic Claude API for LLM extraction — this is a third-party AI API cost that must be estimated carefully. Unlike FleetPulse (which used a self-trained model with no per-inference API cost), TermsIQ has a direct API cost per document processed.

**API cost estimation**

The Claude Sonnet API is used for extraction. A typical car rental T&C document is 5,000–15,000 tokens. At approximately $3 per million input tokens (Claude Sonnet pricing, June 2026):

| Scenario | Documents/month | Avg tokens | Monthly API cost |
|---|---|---|---|
| MVP (50 suppliers, 10 countries each) | 500 initial + ~50 updates | ~10,000 tokens | ~€5–15 (initial batch) + €1–2/mo ongoing |
| Growth (200 suppliers, 20 countries each) | 4,000 initial + ~400 updates | ~10,000 tokens | ~€40–120 (initial) + €4–12/mo ongoing |
| Scale (500 suppliers, 50 countries each) | 25,000 initial + ~2,500 updates | ~10,000 tokens | ~€250–750 (initial) + €25–75/mo ongoing |

**Key insight:** the AI API cost for TermsIQ is remarkably low — because T&C documents change infrequently. The expensive operation (initial extraction across all supplier/country combinations) is a one-time batch. Ongoing cost is driven only by document updates, which are typically a small fraction of total documents per month. The API cost is not the budget risk — the people cost is.

**Full cost model**

| Cost category | MVP (months 1–3) | Growth (months 4–9) | Ongoing /month |
|---|---|---|---|
| **Infrastructure** | | | |
| Claude API (Anthropic) | €15–50 one-off + €2–5/mo | €120–200 one-off + €10–20/mo | €10–75 |
| Cloud hosting (FastAPI, PostgreSQL, storage) | €100–300/mo | €300–800/mo | €300–1,000 |
| Document storage (PDFs, Excel files) | €0–50/mo | €50–150/mo | €50–200 |
| **People** | | | |
| AI/NLP engineer (contract → hire) | €8,000–12,000/mo | €7,000–10,000/mo | €7,000–9,000 |
| Backend engineer (contract → hire) | €6,000–10,000/mo | €6,000–9,000/mo | €6,000–8,000 |
| AI consultant / specialist **[Often missed]** | €5,000–12,000 one-off | €2,000–4,000 (prompt engineering audits) | €500–1,000 |
| **Documentation & compliance** | | | |
| GDPR / data flow documentation **[Often missed]** | €1,000–3,000 one-off | €500/year | €100 |
| Legal review (web scraping, IP, liability) **[Often missed]** | €3,000–8,000 one-off | €1,000/year | €200 |
| EU AI Act classification review **[Often missed]** | €2,000–5,000 one-off | €1,000/year | €100 |
| Audit trail and version history system **[Often missed]** | €2,000–4,000 one-off | €500/mo | €300–500 |
| **Monitoring & maintenance** | | | |
| Extraction accuracy monitoring **[Often missed]** | €0 (built into eng) | €500–1,000/mo | €500–1,000 |
| Model/prompt maintenance **[Often missed]** | €0 (built into eng) | €500–1,000/mo | €500–1,000 |
| **Change management** | | | |
| Content team training and workflow redesign **[Often missed]** | €3,000–5,000 one-off | €500/mo | €200 |
| Supplier communication programme **[Often missed]** | €2,000–4,000 one-off | €500/quarter | €200 |
| Stakeholder validation workshops **[Often missed]** | €2,000–3,000 one-off | €500/quarter | €150 |

**Summary**

| | |
|---|---|
| Total MVP investment | €60,000–110,000 |
| Content team time saving (60% of 1 FTE) | €3,000–5,000/month in labour cost avoided |
| OTA partner dispute reduction value | Estimated €10,000–50,000/month in avoided compensation and relationship cost |
| Break-even point | Month 2–4 after going live |

**Biggest cost optimisation lever:** prompt caching. The system prompt and schema definition are identical for every extraction call. Anthropic's prompt caching feature reduces the cost of repeated context by up to 90%. For a document pipeline processing hundreds of similar documents, this single optimisation can cut API costs by 80%+.

---

### 4.2 The six AI cost optimisation strategies applied to TermsIQ

1. **Cache responses** — identical documents (same PDF, same hash) do not need re-extraction. A document that has not changed since last week costs zero to "re-process."
2. **Prompt caching** — the system prompt, schema definition, and few-shot examples are cached across API calls. Major cost reduction at volume.
3. **Use the right model** — Claude Sonnet is sufficient for structured extraction from well-formatted documents. Claude Opus is only needed for ambiguous, poorly-structured, or multilingual documents where Sonnet's confidence score is below threshold.
4. **Reduce document size before extraction** — strip headers, footers, page numbers, and irrelevant sections (vehicle descriptions, marketing text) before sending to the API. A 15,000-token document may contain only 3,000 tokens of relevant T&C content.
5. **Monitor and alert** — an anomalous spike in API calls likely means the change detection system is triggering on non-material document changes (e.g. a PDF timestamp update). Set minimum diff thresholds before re-extraction is triggered.
6. **Batch processing** — initial extraction across all supplier/country combinations runs as an overnight batch job, not in real time. This avoids API rate limit costs and allows for quality review before data goes live.

---

### 4.3 Change management — addressing the fear of AI replacement

The Content Manager is the stakeholder most directly affected by TermsIQ. Their current role involves significant manual T&C maintenance work — reading PDFs, updating spreadsheets, chasing supplier account managers for updates. TermsIQ automates the majority of this.

#### The reframe: from data entry to data governance

TermsIQ does not eliminate the Content Manager role — it eliminates the low-value parts of it:

- Reading 40-page PDFs in foreign languages looking for a single field value
- Manually re-entering data from supplier emails into a spreadsheet
- Reactively fixing T&C errors after an OTA reports a counter dispute

What it creates — and what becomes more valuable because of it — is a data governance and exception management role:

- Reviewing and approving AI extractions that fall below the confidence threshold
- Managing the supplier relationship around T&C quality — requesting structured data, establishing direct document feeds
- Expanding TermsIQ coverage to new suppliers and new T&C fields
- Interpreting edge cases where T&C language is ambiguous or contradictory

**The honest message to the content team:** TermsIQ handles the reading. You handle the judgement.

#### Three validation workshops

**Workshop 1 — Week 2 — Co-design:** Involve the Content Manager in defining the extraction schema. What does "licence type accepted" mean in practice? What edge cases exist that a simple extraction will miss? Their knowledge directly improves the prompt design and validation rules.

**Workshop 2 — Week 6 — Accuracy review:** Show the Content Manager the extraction results alongside the source documents. Let them challenge the AI on cases they know are complex. Build trust by demonstrating that the human review queue catches the errors before they go live.

**Workshop 3 — Week 10 — Impact review:** Show the measurable reduction in content maintenance hours and the reduction in T&C-related OTA complaints. This is where the Content Manager sees that TermsIQ made them more effective — not redundant.

> **Critical point:** the Content Manager likely knows which supplier T&C documents are reliable and which are notoriously ambiguous. This knowledge — which suppliers use clear structured language, which ones bury critical terms in footnotes, which ones contradict themselves between sections — is invaluable for building a high-quality extraction system. Engage them as the domain expert, not as the person being replaced.

---

### 4.4 Go-to-market

#### Target users

**Primary buyer:** Chief Commercial Officer or Head of Supplier Partnerships at a car rental aggregator API provider. Company size 50–300 employees, managing connectivity for 100–500 suppliers. Currently facing OTA partner complaints about T&C accuracy and regulatory pressure from EU consumer law enforcement.

**Technical evaluator:** CTO / VP Engineering. Evaluates integration complexity, API contract changes, latency impact, and fallback behaviour. Must be satisfied that TermsIQ appends new fields without breaking existing API responses.

**Day-to-day user:** Content Manager / Supplier Content Team. Uses the human review interface daily. Their adoption and trust in the system determines whether the data quality improves or deteriorates over time.

**Decision process:** B2B, sales-led. Decision at CCO/CTO level. Sales cycle 2–4 months. The live demo — uploading a real Hertz or Sixt PDF and showing the structured extraction in seconds — is the most powerful sales moment.

#### Value proposition

> TermsIQ turns unstructured supplier PDFs into structured API data — automatically, in any language, with change detection built in. Your content team stops reading PDFs. Your OTA partners stop receiving complaints about incorrect terms. And your regulators see an aggregator that takes T&C transparency seriously.

#### Channels to reach target buyers

- Direct outreach to Commercial Directors at aggregators and OTAs known to struggle with T&C quality — this is a small, identifiable market
- Travel technology conferences (WTM London, ITB Berlin, Phocuswright Europe) — the T&C problem is widely discussed but unsolved; a demo at a conference creates immediate credibility
- EU regulatory angle — position TermsIQ as the compliance solution to the European Commission's ongoing enforcement action; regulatory affairs teams at aggregators are actively looking for solutions

#### Launch strategy

| Phase | Timing | Goal |
|---|---|---|
| Pilot | Months 1–3 | One pilot client, top 50 supplier/country combinations, shadow extraction running alongside manual process. Measure accuracy and time saving. |
| Validate | Months 4–6 | Live in API for pilot client's OTA partners. Measure counter dispute rate and content team hours. Produce case study. |
| Scale | Months 7+ | Use case study to close second and third clients. Expand to additional T&C fields (fuel policy, cross-border rules, excess amounts). |

#### Success metrics

| Metric | Target |
|---|---|
| Field coverage | ≥90% of active supplier/country combinations within 90 days |
| Extraction accuracy | ≥95% on validated ground truth |
| Content team time saving | ≥60% reduction in manual maintenance hours |
| Counter dispute rate | Measurable reduction reported by OTA partners within 6 months |
| Client expansion | Pilot client adds additional T&C fields or markets by month 6 |

---

## Section 5 — Data Sources & Demo Strategy

### 5.1 Why TermsIQ has no dataset problem

Unlike pricing models that require proprietary historical booking data, TermsIQ's training and demonstration data is the T&C documents themselves — and these are publicly available right now.

Every major car rental supplier publishes their terms and conditions online. Hertz maintains country-specific T&C PDFs at publicly accessible URLs structured as `images.hertz.com/pdfs/RT_FULL_[COUNTRY_CODE]_EN.pdf`. Sixt publishes rental information per country on their website. Avis, Europcar, and Enterprise all publish accessible T&C pages.

This means the demo for Thursday is built from **real supplier documents** — not synthetic data, not proxies, not academic datasets. Real Hertz terms for Spain. Real Sixt terms for Germany. Real Avis terms for the UK. Extracted by the AI. Compared side by side. Served as structured JSON.

### 5.2 Demo data — documents to download today

| Supplier | Country | URL | Key fields to demonstrate |
|---|---|---|---|
| Hertz | Spain | images.hertz.com/pdfs/RT_FULL_ES_EN.pdf | Country-specific TPL, grace period, payment |
| Hertz | Germany | images.hertz.com/pdfs/RT_FULL_DE_EN.pdf | Licence requirements, cross-border rules |
| Hertz | UK | images.hertz.com/pdfs/RT_FULL_GB_EN.pdf | Payment types, deposit rules |
| Sixt | Germany | car-rental.sixt.com/php/terms (DE) | Explicit digital licence rejection, IDP requirements |
| Sixt | Spain | car-rental.sixt.com/php/terms (ES) | Country zone restrictions |
| Avis | Europe general | avis.co.uk/rental-information/terms | Payment policy, age restrictions |

**The demo moment:** paste the Sixt Germany terms URL into the TermsIQ interface. Within seconds the system returns:

```json
{
  "supplier": "Sixt",
  "pickup_country": "DE",
  "extracted_at": "2026-06-19T10:23:00Z",
  "confidence": 0.94,
  "terms": {
    "licence_accepted": {
      "eu_eea_licence": true,
      "digital_licence": false,
      "photocopy_accepted": false,
      "idp_required_for": ["non-EU/EEA licences not in German"],
      "confidence": 0.97
    },
    "payment_accepted": {
      "credit_card_required": true,
      "debit_card": "not_accepted",
      "valid_until_days_after_return": 30,
      "confidence": 0.91
    },
    "grace_period_minutes": null,
    "grace_period_note": "Not specified in document — human review required",
    "grace_period_confidence": 0.20,
    "tpl_amount_eur": null,
    "tpl_note": "Refers to statutory German minimum — COB lookup: €7,500,000 personal injury / €1,300,000 property damage",
    "tpl_confidence": 0.95,
    "cross_border_conditions": {
      "zone_1_permitted": ["Andorra","Austria","Belgium","Denmark","Finland","France","Germany","Gibraltar","Great Britain","Ireland","Italy","Liechtenstein","Luxembourg","Monaco","Netherlands","Norway","Portugal","San Marino","Sweden","Switzerland","Spain","Vatican"],
      "zone_2_permitted_standard_vehicles": ["Croatia","Czech Republic","Poland","Slovakia","Slovenia"],
      "zone_3_permitted_economy_only": ["Estonia","Hungary","Latvia","Lithuania"],
      "zone_4_prohibited": true,
      "confidence": 0.88
    }
  }
}
```

This output does three things at once in the demo: it shows what the AI successfully extracts (licence rules, payment rules), it shows what the AI correctly flags as uncertain (grace period — not specified), and it shows what requires a follow-up document (TPL — refers to statutory minimum). This is honest, defensible, and impressive.

### 5.3 What "training data" means for TermsIQ

TermsIQ is not a traditional ML model trained on labelled examples. It uses a large language model (LLM) with a structured extraction prompt. The "training" is the prompt engineering — defining the schema, providing few-shot examples of correct extractions, and specifying how to handle ambiguity.

The validation dataset — which your instructor will ask about — is a set of manually verified ground truth extractions: for 20–30 supplier/country combinations, a human expert reads the source document and records the correct value for each of the five fields. The AI's extractions are compared against this ground truth to calculate accuracy. This is the evaluation methodology, not a training dataset in the traditional sense.

**For the prototype:** download 6 T&C documents (2 suppliers × 3 countries). Manually extract the five fields from each. Run TermsIQ against the same documents. Compare. Calculate accuracy. That is your validation evidence for Thursday.

### 5.4 Technology stack — all free for the demo

| Component | Tool | Cost |
|---|---|---|
| PDF parsing | PyMuPDF (open source) | Free |
| LLM extraction | Anthropic Claude API (claude-sonnet-4-6) | Free tier / pay-per-use (~€0.10 for demo) |
| Schema validation | Pydantic (Python library) | Free |
| API serving | FastAPI | Free |
| Demo interface | Streamlit | Free |
| Database | SQLite (demo) → PostgreSQL (production) | Free |
| Version control | GitHub | Free |
| Hosting | Streamlit Cloud | Free |

**Total demo cost: approximately €0.10 in API calls.**

### 5.5 Data acquisition by project phase

| Data source | Demo | MVP | Growth | Scale |
|---|---|---|---|---|
| Supplier T&C PDFs | Downloaded manually from public URLs | Direct feed from supplier account managers | Automated crawl + direct feed | Real-time monitoring + direct API from major suppliers |
| Ground truth validation set | 6 documents, manually verified | 50 supplier/country pairs, verified by content team | 200+ pairs, ongoing QA process | Automated accuracy monitoring with human audit sampling |
| Confidence thresholds | Fixed at 0.85 for demo | Tuned based on content team feedback | Dynamically adjusted per field type | Per-supplier, per-language, per-field thresholds |
| Multi-language documents | English only | English + Spanish + German | All EU languages | All languages with regional review |

---

## Appendix A — Extraction schema (v1)

The five T&C fields extracted per supplier × pickup country combination. The four core fields (TPL, grace period, licence, payment) are the primary v1 deliverable. Cross-border conditions are extracted in the same API call and served as a bonus field.

```json
{
  "supplier_id": "string",
  "pickup_country_iso": "string (ISO 3166-1 alpha-2)",
  "source_document_url": "string",
  "source_document_hash": "string (SHA-256 for change detection)",
  "extracted_at": "datetime (UTC)",
  "schema_version": "1.0",
  "terms": {
    "third_party_liability": {
      "amount_eur": "number or null",
      "refers_to_statutory_minimum": "boolean",
      "notes": "string or null",
      "confidence": "float (0.0–1.0)"
    },
    "grace_period": {
      "minutes": "integer or null",
      "airport_specific": "boolean",
      "auto_cancel_if_exceeded": "boolean or null",
      "notes": "string or null",
      "confidence": "float (0.0–1.0)"
    },
    "licence_accepted": {
      "eu_eea_licence": "boolean",
      "uk_licence": "boolean",
      "us_licence": "boolean",
      "international_driving_permit_required": "boolean",
      "digital_licence_accepted": "boolean",
      "photocopy_accepted": "boolean",
      "minimum_years_held": "integer or null",
      "notes": "string or null",
      "confidence": "float (0.0–1.0)"
    },
    "payment_accepted": {
      "credit_card_required": "boolean",
      "debit_card_accepted": "string (yes / prepaid_only / no)",
      "digital_wallet_accepted": "boolean or null",
      "card_valid_days_after_return_required": "integer or null",
      "notes": "string or null",
      "confidence": "float (0.0–1.0)"
    },
    "cross_border_conditions": {
      "permitted_countries": "array of ISO country codes or null",
      "prohibited_countries": "array of ISO country codes or null",
      "authorisation_required": "boolean",
      "vehicle_category_restrictions": "string or null",
      "penalty_eur": "number or null",
      "notes": "string or null",
      "confidence": "float (0.0–1.0)"
    }
  }
}
```

---

## Appendix B — Comparison: TermsIQ vs FleetPulse

| Dimension | TermsIQ | FleetPulse |
|---|---|---|
| Problem type | Document intelligence / NLP | Predictive pricing / tabular ML |
| AI method | LLM extraction (Claude API) | Gradient boosted trees (XGBoost) |
| Training data | Real public supplier PDFs — available today | Proprietary booking history — not publicly available |
| Demo data | Real (Hertz, Sixt, Avis PDFs) | Synthetic or hotel dataset proxy |
| Regulatory driver | EU consumer law enforcement — active and documented | Revenue optimisation — commercially motivated |
| Primary stakeholder pain | Legal liability + content team operational cost | Revenue per search + metasearch competitiveness |
| Build complexity | Medium — LLM + API + UI | High — data pipeline + ML training + A/B testing |
| Time to working demo | 2–3 days | 4–5 days |
| Uniqueness in bootcamp context | High — document AI specific to car rental | Low — pricing model is a common ML project |

---

*TermsIQ — Intelligent Terms & Conditions Extraction for Car Rental Distribution*
*Document version 1.0 — June 2026*

---

## Appendix C — Third Party Liability reference data architecture

### C.1 The official source: Council of Bureaux

The authoritative reference for minimum TPL amounts across all Green Card system countries is the **Council of Bureaux (COB)** — the international organisation that administers the Green Card motor insurance system. COB publishes and periodically updates a document titled "Minimum Amount of Coverage" listing statutory minimums for both personal injury and property damage, per country, in EUR and local currency.

**Official document URL:** `https://www.cobx.org/sites/default/files/2026-04/MinimumAmountOfCoverage%202026.pdf`

The URL contains the year and month of publication — the document is updated periodically and the filename changes. TermsIQ monitors this URL pattern for new editions and re-parses automatically when a new version is detected.

The COB document covers both EEA and non-EEA countries participating in the Green Card system — making it the most comprehensive single reference available. However, as shown below, data completeness and freshness varies significantly by country.

---

### C.2 Actual TPL minimum amounts — key car rental markets (April 2026 edition)

Data extracted directly from the COB April 2026 publication. All amounts in EUR per accident unless otherwise noted.

| Code | Country | Personal injury (per accident) | Property damage (per accident) | COB data date | TermsIQ confidence |
|---|---|---|---|---|---|
| E | Spain | €70,000,000 | €15,000,000 | Dec-25 | High |
| D | Germany | €7,500,000 | €1,300,000 | Dec-25 | High |
| F | France | Unlimited | Unlimited | Mar-22 | Low — stale 2022 |
| I | Italy | €6,450,000 | €1,300,000 | Dec-25 | High |
| P | Portugal | €6,450,000 | €1,300,000 | Dec-25 | High |
| B | Belgium | €129,550,507 | Unlimited | Dec-25 | High |
| NL | Netherlands | €6,070,000 | €1,220,000 | Nov-20 | Low — stale 2020 |
| GR | Greece | €1,300,000 | €1,300,000 | Dec-25 | High |
| DK | Denmark | €18,209,083 | €3,615,039 | Dec-25 | High |
| A | Austria | n/a | n/a | Oct-21 | None — no data |
| HR | Croatia | €6,450,000 | €1,300,000 | Dec-25 | High |
| CY | Cyprus | €38,600,000 | €1,300,000 | Aug-23 | Medium |
| EST | Estonia | €6,450,000 | €1,300,000 | Dec-25 | High |
| H | Hungary | €6,450,000 | €1,300,000 | Sep-21 | Low — stale 2021 |
| L | Luxembourg | Unlimited | Unlimited | Dec-25 | High — but non-numeric |
| LT | Lithuania | €6,450,000 | €1,300,000 | Dec-25 | High |
| LV | Latvia | €6,450,000 | €1,300,000 | Dec-25 | High |
| M | Malta | €6,070,000 | €1,220,000 | Nov-20 | Low — stale 2020 |
| PL | Poland | €5,210,000 | €1,050,000 | Dec-25 | High |
| RO | Romania | €6,070,000 | €1,220,000 | Dec-25 | High |
| S | Sweden | Unlimited | €27,398,511 | Dec-25 | High — but personal injury non-numeric |
| N | Norway | Unlimited | €8,484,643 | Dec-25 | High — but personal injury non-numeric |
| IS | Iceland | €25,134,409 | €2,909,946 | Dec-25 | High |
| CH | Switzerland | €5,325,948 | €5,000,000 CHF per claim | Nov-24 | High |
| UK | United Kingdom | €1,372,056 / £1,200,000 | €1,372,056 / £1,200,000 | Dec-25 | High |
| SK | Slovak Republic | €5,240,000 | €1,050,000 | Dec-25 | High |
| SLO | Slovenia | €6,450,000 | €1,300,000 | Dec-25 | High |
| BG | Bulgaria | €5,327,743 | €1,073,729 | Dec-25 | High |

**Notable values:**
- **Spain (€70M personal injury)** is nearly eleven times the EU MID floor of €6.45M. A supplier T&C referencing "statutory minimum" in Spain means €70M — not the EU floor. This is the clearest example of why the COB lookup is essential.
- **Belgium (€129.5M personal injury, unlimited property damage)** is the highest in the EU — a figure that surprises most industry professionals.
- **France, Luxembourg, Sweden** show unlimited personal injury — legally correct but not displayable as a number in an API response.
- **Austria** has no data submitted to COB. TermsIQ flags this and defers to a direct query of the Austrian national bureau (Verband der Versicherungsunternehmen Österreichs).

---

### C.3 Why this creates a complication — and why that complication is the product

Your point about suppliers not including TPL in their T&C because "it is determined by law" is the most important insight in the TermsIQ design. It means:

**Most supplier T&C documents will not contain a TPL amount.** They will say "third party liability is provided in accordance with applicable local legislation" or simply not mention it. This is legally correct — the supplier is not obliged to repeat the statutory requirement in their rental conditions.

**But the customer needs to know the number.** An OTA that shows nothing, or shows "statutory minimum applies" without resolving what that minimum actually is, has failed the transparency requirement. The EU consumer law enforcement action (55% of intermediaries in violation) is partly driven by exactly this gap.

**TermsIQ's response to this complication:**

1. The LLM extraction detects when a supplier references statutory minimum rather than stating a number — this is recognised as a specific pattern, not a data gap
2. TermsIQ automatically queries the COB reference database for the pickup country
3. The API response returns the resolved national statutory amount, clearly labelled as statutory minimum with the COB as the source and data date
4. For countries where COB data is stale or absent (Austria, France "unlimited", etc.), TermsIQ returns the best available figure with an explicit confidence flag and a link to the COB reference document for the channel partner to handle

This turns a data absence into an intelligent resolution — which is exactly what AI adds that a rule-based system cannot.

---

### C.4 Three-layer TPL resolution logic in the TermsIQ pipeline

```
STEP 1 — Supplier document extraction
  IF supplier_states_explicit_tpl_amount:
    → Use supplier amount (source: supplier T&C)
    → confidence = extraction_confidence_score
  ELIF supplier_references_statutory_minimum:
    → Proceed to Step 2
  ELSE:
    → Flag as not_mentioned, proceed to Step 2

STEP 2 — COB reference lookup
  → Query COB table by pickup_country_iso_code
  IF cob_data_exists AND cob_data_age_months < 18:
    → Return cob_personal_injury_amount + cob_property_damage_amount
    → source = "COB Minimum Amount of Coverage [edition date]"
    → confidence = HIGH
  ELIF cob_data_exists AND cob_data_age_months >= 18:
    → Return cob_amounts with staleness flag
    → confidence = MEDIUM
    → recommend_verification = true
  ELIF cob_value = "unlimited":
    → Return tpl_display = "unlimited"
    → confidence = HIGH (unlimited is correct)
    → note = "No numeric minimum — statutory unlimited coverage"

STEP 3 — Fallback
  IF no_cob_data (e.g. Austria):
    → Return tpl_display = "not_available"
    → source_url = "https://www.cobx.org/sites/default/files/..."
    → flag = requires_manual_verification
    → confidence = NONE
```

---

### C.5 COB document monitoring — TermsIQ update strategy

The COB document filename follows the pattern `MinimumAmountOfCoverage [YEAR].pdf` published at `cobx.org`. TermsIQ monitors this pattern monthly:

1. Check for new edition by probing the expected URL for the current year/month
2. If new edition found: download, parse, extract structured table, diff against previous version
3. Flag any country where amounts changed between editions
4. Alert the content team and update the knowledge base
5. Recalculate confidence scores for all API responses that reference that country

**Important COB disclaimer (from the document itself):** "The amounts are provided for information only, and COB assumes no responsibility for the accuracy of, or future changes in, their values." This means TermsIQ must treat COB data as a high-quality reference, not as a legally guaranteed figure — and must communicate this clearly in the API response metadata.

---

*TermsIQ — Intelligent Terms & Conditions Extraction for Car Rental Distribution*
*Document version 1.1 — June 2026 — Appendix C added*
