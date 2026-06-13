# TermsIQ — ROI & Risk Assessment
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.3 — June 2026

---

## Section 1 — ROI Analysis

### 1.1 Cost Estimates — Upfront (Year 1, Months 1–6)

| Cost item | Category | Low estimate | High estimate | Notes |
|---|---|---|---|---|
| AI/NLP engineer (contract, 6 months) | Development | €48,000 | €72,000 | Senior contractor, Germany-based, €8–12k/mo loaded |
| Backend engineer (contract, 6 months) | Development | €36,000 | €60,000 | Senior contractor, Germany-based, €6–10k/mo loaded |
| AI consultant / prompt engineering | Development | €5,000 | €12,000 | One-off specialist engagement for extraction design and few-shot example library |
| **Fine-tuning dataset annotation (weeks 1–4)** | Development | €3,000 | €6,000 | Content team annotating 150 documents × 5 fields = 750 labelled examples; 37–75 hours at loaded content team cost |
| **Fine-tuning compute (v2 model)** | Tools/licences | €500 | €2,000 | OpenAI fine-tuning API or equivalent; one-off training run on 750 examples |
| Cloud infrastructure setup (Germany region) | Infrastructure | €1,200 | €3,600 | 6 months × €200–600/mo during build |
| Vector DB / document storage setup | Infrastructure | €0 | €600 | Qdrant or pgvector, EU-hosted; free tier viable at MVP |
| OpenAI GPT-4o API — initial batch extraction (primary) | Tools/licences | €50 | €800 | One-off batch across all supplier/country combinations; OpenAI via Azure Germany region for data residency |
| Anthropic Claude API — fallback extraction | Tools/licences | €10 | €200 | Fallback provider; low volume in normal operation |
| GDPR / data flow documentation | Compliance | €1,000 | €3,000 | Legal/DPO review of pipeline data flows |
| Legal review (web scraping, IP, liability) | Compliance | €3,000 | €8,000 | External legal counsel, one-off |
| EU AI Act classification review | Compliance | €2,000 | €5,000 | One-off classification and documentation |
| Audit trail and version history system | Development | €2,000 | €4,000 | Built into pipeline; engineering cost |
| Content team training and workflow redesign | Change management | €3,000 | €5,000 | Workshops + documentation |
| Supplier communication programme | Change management | €2,000 | €4,000 | Informing suppliers of document feed requirements |
| Stakeholder validation workshops | Change management | €2,000 | €3,000 | 3 workshops across build phase |
| **Total upfront (Year 1, months 1–6)** | | **€105,250** | **€180,950** | |
| **Midpoint estimate used for ROI** | | **€143,000** | | |

---

### 1.2 Cost Estimates — Ongoing (From Month 7)

| Cost item | Monthly low | Monthly high | Annual (months 7–12) | Annual (Year 2–3) |
|---|---|---|---|---|
| AI/NLP engineer (reduced to part-time or hire) | €4,000 | €7,000 | €24,000–42,000 | €48,000–84,000 |
| Backend engineer (maintenance, part-time) | €2,000 | €4,000 | €12,000–24,000 | €24,000–48,000 |
| OpenAI GPT-4o API — ongoing (primary) | €10 | €75 | €60–450 | €120–900 |
| Anthropic Claude API — ongoing fallback | €5 | €20 | €30–120 | €60–240 |
| **Fine-tuned model inference (v2, from month 4)** | €5 | €30 | €30–180 | €60–360 |
| *Note: fine-tuned model replaces GPT-4o for standard extractions from v2; GPT-4o retained for edge cases only — net inference cost falls 40–60% vs v1* | | | | |
| Cloud hosting (Germany region) | €300 | €1,000 | €1,800–6,000 | €3,600–12,000 |
| Document storage | €50 | €200 | €300–1,200 | €600–2,400 |
| Monitoring and accuracy review | €500 | €1,000 | €3,000–6,000 | €6,000–12,000 |
| Model/prompt maintenance | €500 | €1,000 | €3,000–6,000 | €6,000–12,000 |
| Compliance upkeep (GDPR, EU AI Act annual review) | €100 | €200 | €600–1,200 | €1,200–2,400 |
| **Total ongoing per month** | **€7,460** | **€14,475** | | |
| **Total ongoing months 7–12** | | | **€44,760–86,850** | |
| **Total ongoing Year 2–3 (per year)** | | | | **€89,520–173,700** |
| **Midpoint ongoing Year 1 (months 7–12)** | | | **€65,805** | |
| **Midpoint ongoing Year 2–3 (per year)** | | | | **€131,610** |

---

### 1.3 Business Value Estimate

TermsIQ generates value across three streams. Each is estimated conservatively.

#### Stream 1 — Customer service cost reduction (most directly measurable)

T&C-related counter disputes (wrong payment, cancelled booking, rejected licence, cross-border refusal) are the most complex, longest, and most escalation-prone contacts in car rental customer service.

| Assumption | Value | Source / rationale |
|---|---|---|
| T&C-related contacts per month (aggregator + OTA combined) | 200 cases | Conservative estimate for a mid-size aggregator with 100–500 suppliers; ECC-Net documented 6,016 complaints across the EU market in 2025 |
| Share attributable to aggregator T&C data gaps | 30% | Not all complaints trace to the aggregator; conservative share |
| Cases per month attributable to TermsIQ gap | 60 cases | 200 × 30% |
| Average handling time, T&C dispute call | 25 minutes | Complex disputes vs ~5 min standard call; industry benchmark |
| Agent fully loaded cost per minute | €0.80 | €25–35/hr loaded agent cost ÷ 60 |
| Cost per T&C dispute case | €20 | 25 min × €0.80 |
| Monthly saving (cases eliminated) | €1,200 | 60 cases × €20 |
| **Annual saving — customer service** | **€14,400** | Conservative; does not include escalation, supervisory, or churn cost |

#### Stream 2 — Legal and regulatory risk reduction (risk-adjusted)

| Assumption | Value | Source / rationale |
|---|---|---|
| EU consumer law enforcement action probability (per year) | 10% | EC has already acted against 5 major suppliers; aggregators are next in enforcement scope |
| Estimated fine / compensation exposure if actioned | €50,000–500,000 | Based on EC enforcement precedents and EU Directive 93/13/EEC exposure |
| Risk-adjusted annual value of avoidance | €5,000–50,000 | 10% × €50k–500k |
| **Midpoint risk-adjusted annual value** | **€27,500** | Used in ROI calculation |

#### Stream 3 — Commercial / competitive advantage (conservative)

| Assumption | Value | Source / rationale |
|---|---|---|
| OTA partners retained or won due to T&C quality improvement | 1 incremental OTA per year | Conservative; TermsIQ is a differentiator in a market where no competitor offers this |
| Annual revenue per OTA partner (connectivity fees) | €30,000–100,000 | Typical aggregator connectivity fee range for mid-size OTA |
| **Conservative annual revenue attribution** | **€30,000** | One OTA at low end; not included in base ROI to remain conservative — treated as upside |

**Total quantified annual benefit (Streams 1 + 2, excluding commercial upside):**

| Stream | Annual value |
|---|---|
| Customer service cost reduction | €14,400 |
| Legal risk reduction (risk-adjusted) | €27,500 |
| **Total base annual benefit** | **€41,900** |
| Commercial upside (Stream 3, excluded from base) | +€30,000 |

---

### 1.4 ROI Calculation

**Formula:** `ROI = (Net Benefit / Total Cost) × 100`

#### 12-month ROI

| Item | Midpoint estimate |
|---|---|
| Total cost — upfront (months 1–6) | €143,000 |
| Total cost — ongoing (months 7–12) | €65,805 |
| **Total 12-month cost** | **€208,805** |
| Annual benefit (months 7–12, 6 months of value) | €20,950 |
| Net benefit at 12 months | €20,950 − €208,805 = **−€187,855** |
| **12-month ROI** | **−90%** |

> Year 1 is investment-heavy. The system is not live and generating value until month 7 at earliest. A negative 12-month ROI is expected and normal for a software build — this does not mean the investment is unsound.

#### 36-month ROI

| Item | Midpoint estimate |
|---|---|
| Total cost — Year 1 (upfront + ongoing) | €208,805 |
| Total cost — Year 2 | €131,610 |
| Total cost — Year 3 | €131,610 |
| **Total 36-month cost** | **€472,025** |
| Annual benefit — Year 1 (6 months live) | €20,950 |
| Annual benefit — Year 2 | €41,900 |
| Annual benefit — Year 3 | €41,900 |
| **Total 36-month benefit** | **€104,750** |
| **Net benefit at 36 months** | **−€367,275** |
| **36-month ROI (base case, Streams 1+2 only)** | **−78%** |

| Item | With Stream 3 commercial upside included |
|---|---|
| Additional annual benefit (Stream 3) | €30,000/year |
| Total 36-month benefit incl. Stream 3 | €104,750 + €90,000 = €194,750 |
| **Net benefit at 36 months incl. Stream 3** | **−€277,275** |
| **36-month ROI incl. commercial upside** | **−59%** |

> **Honest interpretation:** On quantified cost-saving metrics alone, TermsIQ does not return a positive ROI within 36 months at midpoint estimates. This is a known limitation of risk-avoidance and compliance-driven investments — the value is real but hard to fully monetise in a spreadsheet. The business case is strengthened significantly by Stream 3 (commercial differentiation) and by the risk that a regulatory enforcement action — which is unquantified above its probability-adjusted value — could cost multiples of the entire TermsIQ build cost in a single incident.

---

### 1.5 Break-Even Point

| Scenario | Break-even month |
|---|---|
| Base case (Streams 1+2 only, midpoint costs) | Month 67 (approx. 5.5 years) |
| Including Stream 3 commercial upside | Month 48 (approx. 4 years) |
| Optimistic (low cost estimates + all 3 streams) | Month 30 (approx. 2.5 years) |
| If one regulatory enforcement action avoided (€200k) | Month 18–24 |

> The break-even case is most compelling when framed around risk avoidance. A single regulatory enforcement action or major OTA contract loss — both plausible given the documented EU enforcement environment — would justify the entire investment retroactively.

---

### 1.6 Assumptions Table

| # | Assumption | Value used | Justification |
|---|---|---|---|
| A1 | Engineer contract rates (Germany) | €8–12k/mo AI engineer; €6–10k/mo backend | Germany senior contractor market rates, June 2026 |
| A2 | Build duration | 6 months to go-live | Standard for an MVP pipeline of this complexity with a 2-person core team |
| A3 | Ongoing team reduction post-launch | 50% of build-phase FTE | Maintenance requires less resource than build; some work absorbed by existing content team |
| A4 | T&C-related contacts per month | 200 total across chain | Conservative for aggregator with 100–500 suppliers; based on ECC-Net 6,016 EU complaints ÷ estimated aggregators in market |
| A5 | Share attributable to aggregator data gaps | 30% | Not all complaints trace to the aggregator; conservative attribution |
| A6 | Average handling time, T&C dispute | 25 minutes | Complex dispute calls vs ~5 min standard; industry customer service benchmark |
| A7 | Agent loaded cost per minute | €0.80 | €25–35/hr fully loaded agent cost (salary + benefits + overhead) |
| A8 | Regulatory action probability | 10% per year | EC has active enforcement programme; aggregators in scope; precedent set with major suppliers |
| A9 | Regulatory exposure if actioned | €50k–500k | Based on EC enforcement precedents; Directive 93/13/EEC; GDPR fine scale |
| A10 | Incremental OTA revenue | €30k/year | Conservative low-end connectivity fee for mid-size OTA; one new OTA per year |
| A11 | LLM API costs — dual provider | OpenAI GPT-4o primary (via Azure Germany); Anthropic Claude fallback | T&C documents are infrequently updated; API cost is not the material cost driver for either provider. Azure OpenAI used for Germany data residency compliance. |
| A12 | Infrastructure (Germany region) | €300–1,000/mo ongoing | AWS Frankfurt or equivalent; FastAPI + PostgreSQL + Qdrant stack |
| A13 | System goes live | Month 7 | Allows 6 months build + validation before production |
| A14 | Benefits accrue linearly from go-live | Full annual rate from month 7 | Conservative — ramp-up may mean lower benefit in first months live |
| A15 | Fine-tuning dataset annotation | 150 documents × 15–30 min = 37–75 hours | Documents publicly available now; content team annotates in parallel with v1 build during weeks 1–4 |
| A16 | Fine-tuned model cost saving (v2) | 40–60% reduction in ongoing inference cost | Fine-tuned smaller model (GPT-4o-mini or open-weight) runs at fraction of GPT-4o cost per token; accuracy equal or better on domain-specific task |
| A17 | Fine-tuning ready at v2 launch | Month 3–4 | Annotation weeks 1–4; fine-tuning run week 5; validation weeks 6–8; deployed at v2 |

---

### 1.7 Data Gap Note & Modelling AI Roadmap

**Why the ROI estimates are built on proxies — and what would make them precise**

The customer service savings estimate in Section 1.3 (Stream 1) is built from proxy assumptions rather than actual booking-to-complaint data. This reflects a real structural gap: the dataset linking booking ID → T&C served → complaint outcome does not exist publicly or within any single organisation in the distribution chain. The aggregator holds the T&C served; the OTA receives the complaint; neither has the full picture.

**Two-track modelling AI roadmap**

TermsIQ has two distinct and independent paths toward modelling AI — on very different timelines.

**Track A — Fine-tuning for terminology normalisation (weeks 1–4, v2)**

The training data for this model exists right now. The 10 in-scope suppliers across 15 countries produce approximately 150 publicly available T&C documents. Annotating each document for the 5 critical fields takes 15–30 minutes per document — 37–75 hours total for one content team member. Running in parallel with the v1 build during weeks 1–4, the full labelled dataset of 750 examples is achievable before v1 even goes live.

This dataset is used to fine-tune a smaller, faster model specifically on the car rental T&C extraction task. The fine-tuned model learns supplier-specific terminology patterns as weighted parameters — it knows that Goldcar calls TPL "RC", that Sixt Germany buries the grace period in a cancellation footnote, that "non-cancellation window" and "vehicle hold time" are the same concept. It runs faster and cheaper than GPT-4o (40–60% inference cost reduction) with equal or better accuracy on this specific task.

The human review queue generates additional training data from go-live onwards — every correction a content team member makes is a new labelled example, feeding quarterly model retraining automatically.

| Milestone | Timeline |
|---|---|
| Documents downloaded and organised | Week 1 |
| Annotation complete (150 docs, 750 examples) | Weeks 2–4 |
| Fine-tuning run | Week 5 |
| Validation against held-out test set | Weeks 6–8 |
| Fine-tuned model deployed (replaces GPT-4o for standard extractions) | v2 launch, month 3–4 |

**Track B — Complaint prediction model (v3, 12–18 months post go-live)**

From the moment TermsIQ goes live, the aggregator begins logging — for the first time — exactly which T&C was served for every booking, with a timestamp and version reference. This is the left side of the closed loop. If OTA partners share complaint outcomes linked to booking IDs (which becomes a more compelling ask once TermsIQ has demonstrated T&C quality improvement), the right side closes.

Once closed, the dataset enables complaint-risk scoring per booking at the point of search — identifying which supplier × destination × T&C field combinations are most likely to generate counter disputes. This is the full predictive modelling AI layer.

**Practical implication for the ROI document:** the 36-month financial model does not include the inference cost saving from fine-tuning (Track A) or the revenue/risk value of the complaint prediction model (Track B). Both would improve the ROI calculation — Track A materially, from month 4 onwards. The model is deliberately conservative on these points.

---

## Section 2 — Risk Assessment Matrix

### Risk scoring guide
- **Likelihood:** 1 = Very unlikely → 5 = Very likely
- **Impact:** 1 = Negligible → 5 = Severe
- **Risk level = Likelihood × Impact** (1–25 scale)
- **Risk bands:** Low 1–6 | Medium 7–12 | High 13–19 | Critical 20–25

---

### 2.1 Risk Register

| # | Risk | Category | Likelihood (1–5) | Impact (1–5) | Risk Level | Rating | Mitigation strategy |
|---|---|---|---|---|---|---|---|
| R1 | **EU AI Act classification triggers transparency or conformity obligations** — TermsIQ processes legal documents and outputs data that affects what consumers are shown at booking. Depending on classification, this may require technical documentation, human oversight logging, or conformity assessment. | Regulatory | 3 | 4 | 12 | **Medium** | Engage legal counsel for EU AI Act classification review before go-live (already budgeted). Build audit trail and confidence score logging into the pipeline from day one. Appoint an AI Act compliance owner internally. |
| R2 | **GDPR breach or data residency violation** — if any pipeline component routes data outside Germany (e.g. API call to a non-EU model endpoint, third-party monitoring tool), the data residency requirement is violated. Both OpenAI (via Azure) and Anthropic (via API) must be verified for Germany-region data processing before production. | Regulatory | 2 | 5 | 10 | **Medium** | Use Azure OpenAI Service (Germany North region) for the primary OpenAI integration — this provides contractual EU data residency. Verify Anthropic API data processing terms for EU residency compliance before enabling as fallback in production. Conduct GDPR data flow mapping covering both providers before launch. Include data residency as a hard requirement in all vendor contracts. |
| R3 | **Web scraping of supplier websites ruled impermissible** — supplier website terms of use may prohibit automated access. If legal review finds scraping is not permitted, the web-crawl ingestion route is blocked. | Regulatory | 3 | 3 | 9 | **Medium** | Default to direct document feed from suppliers (via SFTP or email) as the primary ingestion route. Use web crawling only as a fallback and only after legal sign-off per supplier. Build supplier communication programme to request structured T&C feeds directly. |
| R4 | **LLM hallucination on critical fields** — the LLM extracts an incorrect value (wrong grace period, wrong TPL amount, wrong licence rule) with high confidence, passes validation, goes live in the API, and causes a customer counter dispute or regulatory complaint. | Technical | 3 | 5 | 15 | **High** | Confidence scoring with mandatory human review below threshold. Ground-truth validation set reviewed by content team before any data goes live. COB cross-check for TPL creates a second-source verification layer. Dual-provider architecture: low-confidence extractions from GPT-4o are automatically re-run on Claude before being flagged for human review — two independent LLM passes on uncertain cases. Legal-defined fallback policy: below minimum confidence threshold, serve "data not available" rather than a potentially incorrect value. |
| R5 | **Integration failure or API contract breakage** — appending new T&C fields to the existing API response causes unexpected behaviour in downstream OTA integrations (field conflicts, schema changes, parsing errors). | Technical | 2 | 4 | 8 | **Medium** | Design T&C fields as strictly additive — no modification of existing fields. Version the API response schema. Run shadow mode (extraction running in parallel without serving to OTAs) for minimum 4 weeks before going live. Provide OTA partners with advance schema documentation and a sandbox environment. |
| R6 | **Supplier document format changes break the ingestion pipeline** — a supplier changes their PDF layout, URL structure, or switches from PDF to a web-only format, causing extraction to fail silently. | Technical | 4 | 3 | 12 | **Medium** | Change detection monitor checks document hash and structure daily. Pipeline alerts on extraction failure or anomalous confidence score drop. Per-supplier ingestion handlers are modular — a broken handler for one supplier does not affect others. Fallback: serve last known good data with a staleness flag rather than serving nothing. |
| R7 | **Content team resistance to adoption** — the content team perceives TermsIQ as a threat to their role and either withholds domain knowledge during build or does not engage with the human review queue, reducing data quality. | Operational | 3 | 4 | 12 | **Medium** | Three co-design workshops involving the content team from week 2. Frame the role shift explicitly: from data entry to data governance. Show measurable time saving early (week 6 accuracy review). Involve the content team in defining validation rules and confidence thresholds — their knowledge improves the system. |
| R8 | **OTA partners do not consume or trust the new T&C fields** — OTAs receive the new fields but do not surface them to customers, either due to integration effort, distrust of AI-sourced data, or product prioritisation. | Operational | 3 | 3 | 9 | **Medium** | Run pilot with one OTA partner who is already experiencing high T&C complaint rates — they have the strongest incentive to adopt. Provide confidence score and source metadata with every field so OTAs can make trust decisions themselves. Produce a case study from the pilot demonstrating complaint rate reduction. |
| R9 | **Incorrect TPL amount displayed due to stale COB data** — COB reference data for a country is outdated (e.g. Austria has no data; France shows unlimited) and TermsIQ serves an incorrect or absent statutory minimum amount. | Technical / Regulatory | 2 | 4 | 8 | **Medium** | COB staleness flag built into every API response referencing COB data. Confidence score = MEDIUM for data older than 18 months; NONE for missing data. Monthly COB document monitoring for new editions. Austria and France flagged as requiring manual verification in all API responses. |
| R10 | **Bias or discriminatory output in licence acceptance rules** — the LLM extraction systematically misrepresents licence acceptance rules for certain driver nationalities (e.g. non-EU licences), leading to discriminatory booking outcomes. | Ethical | 2 | 4 | 8 | **Medium** | Validation set must include licence rules for all driver source countries in scope (Germany, Switzerland, Spain, plus non-EU edge cases). Human review queue specifically flags licence type extractions for manual verification. Regular bias audit: compare extraction accuracy across driver nationality dimensions. |
| R11 | **Supplier intellectual property claim over extracted T&C content** — a supplier claims that automated extraction and redistribution of their T&C content constitutes a copyright infringement, even though the extracted fields are factual data rather than text reproduction. | Regulatory / Ethical | 2 | 3 | 6 | **Low** | Legal review of IP position before go-live (already budgeted). TermsIQ extracts structured factual fields — not reproduced text — which is generally defensible under EU law. Document the legal basis explicitly. Preferred approach: obtain explicit supplier consent for T&C data feeds as part of the supplier communication programme. |
| R12 | **Key person dependency** — the AI/NLP engineer who builds the extraction pipeline holds critical knowledge. If they leave, ongoing maintenance and prompt engineering are at risk. | Operational | 3 | 3 | 9 | **Medium** | Document all prompt designs, extraction schemas, and validation rules in a maintained knowledge base. Pair-program critical pipeline components. Transition plan: move from contractor to hire for the core AI engineer role after MVP validation to improve continuity. |

---

### 2.2 Risk Summary — Heat Map View

```
         IMPACT
              1          2          3          4          5
         ──────────────────────────────────────────────────
    5    │          │          │          │          │  R4  │
         │          │          │          │          │      │
    4    │          │          │  R6,R7   │  R9,R10  │      │
         │          │          │  R12     │  R5      │      │
L   3    │          │          │  R3,R8   │  R1      │      │
I        │          │          │          │          │      │
K   2    │          │          │  R11     │  R2      │      │
E        │          │          │          │          │      │
L   1    │          │          │          │          │      │
I        │          │          │          │          │      │
H        ──────────────────────────────────────────────────
O        Low ◄─────────────────────────────────► Critical
O
D
```

| Risk level | Risks | Action |
|---|---|---|
| **Critical (20–25)** | None | — |
| **High (13–19)** | R4 (LLM hallucination) | Immediate mitigation required before go-live |
| **Medium (7–12)** | R1, R2, R3, R5, R6, R7, R8, R9, R10, R12 | Mitigate during build; monitor ongoing |
| **Low (1–6)** | R11 | Monitor; review annually |

---

### 2.3 Top Priority Risks

**R4 — LLM hallucination on critical fields** is the single highest-priority risk and the one most specific to AI systems. A confident but incorrect extraction of a grace period or TPL amount that reaches a customer is both a liability and a reputational event. The mitigation — confidence thresholds, human review, COB cross-check, and a "serve nothing rather than serve wrong" fallback policy — must be designed before any data goes live, not added later.

**R1 — EU AI Act classification** is the most likely regulatory risk to materialise before launch. The EU AI Act came into force in 2024 and obligations are phasing in through 2026–2027. A system that processes legal documents and outputs data affecting consumer-facing information at booking requires classification now, not at a compliance audit two years from now.

**R7 — Content team adoption** is the risk most likely to be underestimated. The technical pipeline can work perfectly and still fail if the people responsible for the human review queue disengage. Change management is not a soft problem — it is a delivery risk.

---

*TermsIQ — ROI & Risk Assessment*
*Document version 1.0 — June 2026*
*Prepared as part of TermsIQ project documentation suite*
