# TermsIQ — EU AI Act Compliance Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.0 — June 2026

---

## Section 1 — Risk Classification

### 1.1 Classification outcome

| | |
|---|---|
| **System name** | TermsIQ |
| **System version** | v1 |
| **Classification** | **Limited Risk** |
| **Applicable obligations** | Transparency obligations (Article 50 EU AI Act) |
| **High-risk classification** | Not applicable — see reasoning in Section 1.2 |
| **Date of classification** | June 2026 |
| **Classification owner** | Compliance Officer / Legal |
| **Next review date** | June 2027 or upon material change to system scope |

---

### 1.2 Classification reasoning — step by step

The EU AI Act establishes a tiered risk framework. Classification proceeds by testing each tier in descending order: Unacceptable → High → Limited → Minimal. TermsIQ is assessed at each tier below.

---

#### Step 1 — Unacceptable risk (Article 5)?

Unacceptable risk AI systems are prohibited outright. Examples include: subliminal manipulation, social scoring, real-time biometric surveillance in public spaces, exploitation of vulnerabilities of specific groups.

**TermsIQ assessment:** TermsIQ extracts structured commercial data from supplier documents. It does not manipulate behaviour, score individuals, perform biometric identification, or target vulnerable groups.

**Result: ❌ Not unacceptable risk. Proceed to Step 2.**

---

#### Step 2 — High risk (Annex III)?

High-risk AI systems include those used in: biometric identification, critical infrastructure, education, employment, essential private and public services, law enforcement, migration, administration of justice, and — most relevantly — **systems that affect access to essential private services**.

The key question for TermsIQ is whether it falls under **Annex III, point 5(b)**: *"AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score"* — or point **5(f)**: *"AI systems intended to be used to make decisions or to assist in making decisions relating to persons for access to private services."*

**TermsIQ assessment:**

TermsIQ does **not** make decisions about individuals. It extracts and structures factual data from supplier commercial documents (PDFs, web pages, Excel files). The output is structured T&C data served through a B2B aggregator API to OTA partners. No individual consumer is profiled, scored, assessed, or subject to a decision made by TermsIQ. The system operates entirely at the B2B layer — between the aggregator and its channel partners.

The extracted data (TPL amounts, grace periods, licence rules, payment rules, cross-border conditions) is informational content that describes supplier policies. It does not determine whether any individual can rent a car, receive a service, or access a product.

Additionally, TermsIQ does not appear in any other Annex III category:
- It is not a biometric system
- It is not used in critical infrastructure
- It is not used in education or employment
- It is not used by law enforcement or migration authorities
- It is not used for administration of justice

**Result: ❌ Not high risk. Proceed to Step 3.**

---

#### Step 3 — Limited risk (Article 50)?

Limited risk applies to AI systems that interact with humans in ways where transparency is required:
- Chatbots / conversational AI systems interacting with natural persons
- AI-generated content (deepfakes, synthetic media)
- Emotion recognition systems
- **Systems that generate or manipulate content that could be mistaken for human-generated output**

TermsIQ uses an LLM (OpenAI GPT-4o-mini via Azure Germany North) to read and extract content from documents. The outputs are structured JSON data fields served via API — not text presented to consumers as if written by a human. However, the system:

1. Uses generative AI models to produce structured outputs
2. Serves those outputs through a chain that ultimately reaches consumer-facing booking interfaces
3. Generates content (extracted T&C fields) that consumers and OTAs rely on to make decisions

Under Article 50(1), providers of AI systems that **generate content** must ensure the output is **marked as AI-generated** where this is not evident from context. The API response metadata includes a `source` field (e.g. "AI-extracted from supplier T&C, [date]") and a `confidence_score` — which fulfils this in the B2B context.

Under Article 50(4), users deploying AI systems that generate text published to inform the public on matters of public interest must disclose that the text is AI-generated. OTA partners displaying TermsIQ-sourced T&C data to customers should be advised to label it appropriately.

**Result: ✅ Limited risk applies. TermsIQ has transparency obligations under Article 50.**

---

#### Step 4 — Minimal risk?

Minimal risk systems (spam filters, AI in video games, etc.) have no mandatory obligations. TermsIQ does not fall into this category — its outputs reach consumer-facing interfaces and carry regulatory relevance under EU consumer law.

**Final classification: Limited Risk — Article 50 transparency obligations apply.**

---

### 1.3 Classification notes and caveats

| Issue | Assessment |
|---|---|
| **Future scope expansion** | If TermsIQ is extended to make individualised recommendations (e.g. "this customer's licence will be rejected at this supplier") it would require reclassification and likely High Risk assessment |
| **EU AI Act evolution** | The Act's implementing acts and guidelines are still being published as of June 2026. This classification should be reviewed against any new guidance on LLM-based extraction systems |
| **OTA partner obligations** | OTA partners consuming TermsIQ data via API and displaying it to consumers may have their own transparency obligations under Article 50. The aggregator should include guidance on this in OTA partner contracts. TermsIQ is B2B2C by design, the COB disclaimer is a direct consequence of that indirect consumer exposure, and OTA partners consuming the API inherit a transparency obligation toward end consumers under Article 50(4).  |
| **GPAI model obligations** | OpenAI GPT-4o-mini is a General Purpose AI (GPAI) model subject to its own obligations under the EU AI Act (Articles 51–56). The aggregator's obligation is to use a compliant GPAI provider — which OpenAI via Azure represents |

---

## Section 2 — Mandatory Requirements Summary (Limited Risk)

Limited risk systems are not subject to the full high-risk obligations of Chapter III. However, the following requirements apply and TermsIQ is designed to address them.

---

### 2.1 Transparency obligations (Article 50)

| Obligation | How TermsIQ addresses it |
|---|---|
| AI-generated content must be labelled where not self-evident | Every API response field includes `extraction_method: "AI"`, `source_document`, `extracted_at` timestamp, and `confidence_score`. The B2B context makes AI generation evident; the metadata makes it explicit |
| OTA partners must be informed that content is AI-generated | Included in API documentation and recommended for inclusion in OTA partner contracts. OTAs displaying the data to consumers should label it as AI-sourced |
| Conversational AI must identify itself as AI | Not applicable — TermsIQ is not a conversational system |

### 2.2 Data and data governance

Although not mandatory under Limited Risk classification, TermsIQ implements the following as good practice and in preparation for potential reclassification:

| Requirement | TermsIQ approach |
|---|---|
| Training data relevance | TermsIQ does not train models — it uses pre-trained GPAI models via API. No training data governance obligation applies to the aggregator |
| Input data quality | Supplier documents are versioned and stored. Each extraction is traceable to a specific source document version |
| Data residency | All data stored and processed in Germany. Azure OpenAI (Germany North) used for primary LLM inference |
| Audit trail | Every extraction is timestamped, versioned, and linked to its source document. The knowledge base retains full version history |

### 2.3 Human oversight mechanisms

| Mechanism | Implementation |
|---|---|
| Human review queue | All extractions below the confidence threshold are held in a review queue before going live in the API |
| Mandatory review before go-live | No extracted field enters the production API without passing either automated validation or human sign-off |
| Fallback to "not available" | Below minimum confidence threshold, the API returns `data_not_available` rather than a potentially incorrect value |
| Accuracy audit | Regular spot-checks of live extractions against source documents by the content team |
| Change detection review | When a supplier document changes, the diff is reviewed before the updated extraction goes live |

### 2.4 Transparency and information obligations

| Obligation | Implementation |
|---|---|
| API consumers informed of AI involvement | API documentation states that T&C fields are AI-extracted and includes the confidence scoring methodology |
| Source attribution | Every field in the API response carries a `source` tag (supplier document URL or COB reference) and an `extracted_at` date |
| Confidence disclosure | `confidence_score` (HIGH / MEDIUM / LOW / NONE) and `recommend_verification` flag included in every field response |
| COB data disclaimer | API responses sourced from COB carry the COB disclaimer: figures are provided for information only |

### 2.5 Accuracy and robustness

| Requirement | Implementation |
|---|---|
| Accuracy targets | ≥95% extraction accuracy on the 5 critical fields, validated against manually verified ground truth |
| Wrong-information-to-customer risk | The highest consumer-facing risk: an incorrect extraction displayed at booking causes a counter dispute with no customer recourse. Mitigated by: confidence thresholds + human review gate (no field goes live unvalidated); COB cross-check for TPL; `data_not_available` fallback below minimum confidence; source and confidence metadata in every API response so OTA partners can make trust decisions |
| Confidence scoring | Probabilistic confidence attached to every field; low-confidence outputs do not reach production |
| Supplier format resilience | Modular per-supplier ingestion handlers — a format change at one supplier does not affect others |
| COB cross-check | Independent second-source verification for TPL amounts reduces single-model error risk |
| Nightly batch design | Extraction runs overnight, not in real time — errors are caught in the human review queue before any customer sees the data |

### 2.6 Cybersecurity considerations

| Risk | Mitigation |
|---|---|
| Unauthorised access to extracted T&C knowledge base | Access controls on the database; read-only API tokens for OTA partners; write access restricted to the pipeline and authorised content team |
| Prompt injection via supplier documents | Supplier documents treated as untrusted input; extraction prompts are system-controlled and not exposed to document content influence on system behaviour |
| API key exposure (OpenAI) | Keys stored in environment secrets manager (e.g. AWS Secrets Manager, Germany region); not hardcoded; rotated quarterly |
| Provider incident monitoring | Nightly batch design means an LLM provider outage causes a one-night extraction delay — acceptable given T&C documents do not change daily. Batch retries the following night automatically. |
| Supplier document tampering | Document hash stored at ingest; any re-ingestion checks hash against stored value to detect tampering |

---

## Section 3 — Conformity Assessment Summary

**TermsIQ — Limited Risk AI System**
**Conformity Assessment Summary — June 2026**

---

### 3.1 What the system does

TermsIQ is an AI-powered document intelligence pipeline operated by a car rental API aggregator headquartered in Germany. The system automatically extracts structured, machine-readable terms and conditions data from unstructured supplier source documents — including PDFs, Excel files, XML feeds, and web pages — in any language, and serves the extracted data through the aggregator's existing B2B API infrastructure to downstream booking channel partners (OTAs, airline ancillary platforms, travel management companies).

The system uses a large language model (OpenAI GPT-4o-mini via Azure Germany North) to read supplier documents and extract five critical data fields: third-party liability (TPL) coverage amounts, vehicle pickup grace periods, driver licence type acceptance rules, payment method acceptance rules, and cross-border rental conditions. For TPL, the system cross-references statutory minimum amounts from the Council of Bureaux (COB) Minimum Amount of Coverage reference document where supplier documents reference statutory minimums rather than explicit figures.

A key risk inherent to this system is **the downstream impact of incorrect AI extraction on end customers**. Extracted T&C data is displayed at the point of booking by OTA partners. A customer who acts on incorrect information — arriving at the counter with an unaccepted payment card, an unaccepted licence, or without cross-border authorisation — has no recourse once the rental contract is refused. This risk is addressed through mandatory confidence thresholds, human review gates, and a "serve nothing rather than serve wrong" fallback policy (see Section 2.3 and 2.5).

All data processing and storage occurs within Germany. The system serves output in English (primary) and German (secondary). It operates entirely at the B2B layer and does not interact directly with end consumers.

---

### 3.2 Risk class and basis for classification

| | |
|---|---|
| **Risk classification** | Limited Risk |
| **Applicable provision** | Article 50, EU AI Act (Regulation (EU) 2024/1689) |
| **Basis** | TermsIQ uses generative AI models to produce structured content that ultimately informs consumer-facing information displayed at booking. Transparency obligations apply. The system does not fall within Annex III high-risk categories — it makes no decisions about individuals, performs no biometric identification, and operates exclusively at the B2B aggregator layer. |
| **High-risk exclusion basis** | No Annex III category applies: the system does not assess individuals, affect access to essential services for natural persons, or operate in any of the enumerated high-risk domains (biometrics, critical infrastructure, education, employment, law enforcement, migration, justice). |
| **Role under EU AI Act** | The aggregator operating TermsIQ is the **provider** under Article 3(3) — it places an AI system on the market and makes it available to others under its own name. OTA partners consuming the API are **deployers** under Article 3(4) — they use the AI system in their own business context. This distinction is critical: the aggregator as provider carries primary responsibility for technical documentation, transparency obligations, post-market monitoring, and provider liability. OTA partners as deployers carry responsibility for how they use and display the output to end consumers, including their own Article 50(4) transparency obligations toward customers. |

---

### 3.3 Applicable obligations and design responses

| Obligation | Legal basis | Design response | Status |
|---|---|---|---|
| Label AI-generated content | Art. 50(1) | Every API response field carries `extraction_method`, `source`, `extracted_at`, and `confidence_score` metadata | ✅ Addressed in design |
| Inform downstream users (OTAs) of AI involvement | Art. 50(4) | API documentation states AI extraction methodology; OTA contract clause **mandatory** (not recommended) — see Gap G1 | ⚠️ Contract clause pending |
| Human oversight of outputs | Good practice / Art. 50 context | Human review queue for low-confidence extractions; no field goes live without validation | ✅ Addressed in design |
| Data residency (GDPR / national law) | GDPR Art. 46 / German data law | Azure OpenAI Germany North; all infrastructure Germany-region | ✅ Addressed in design |
| GPAI provider compliance | Art. 51–56 (provider obligation) | OpenAI is subject to GPAI obligations as model provider; aggregator uses it as deployer of the GPAI model | ✅ Provider obligation, not aggregator |
| EU AI Act registration (if required) | Art. 49 | Not required for Limited Risk systems | ✅ Not applicable |
| Post-market monitoring | Art. 72 (provider obligation) | Plan to be documented before go-live — see Gap G4. LangSmith tracing provides the per-run data infrastructure | ⚠️ Plan pending — see G4 |

---

### 3.4 Gaps and resolution plan

| Gap | Description | Resolution | Target |
|---|---|---|---|
| **G1 — OTA partner transparency obligation** | OTA partners are not yet contractually required to label TermsIQ-sourced T&C data as AI-generated when displaying it to consumers. As provider under Article 50(4), the aggregator has an obligation to ensure downstream deployers inform consumers — this cannot be a recommendation, it must be a contractual requirement. | Update OTA partner API agreements to include a **mandatory** transparency clause requiring consumer-facing labelling of AI-extracted T&C content. Non-compliance should be a breach of the API agreement. | Before API go-live to OTA partners |
| **G2 — Formal EU AI Act classification documentation** | This document represents an internal classification assessment. It has not been reviewed by external legal counsel specialising in EU AI Act compliance. | Commission external AI Act legal review as part of the compliance budget (already budgeted at €2,000–5,000 in the ROI document) | Within 90 days of system build commencement |
| **G3 — Scope change monitoring** | If TermsIQ scope expands to individualised recommendations (per-booking licence rejection prediction, per-driver risk scoring), the classification must be revisited and may become High Risk. | Establish a scope change review trigger: any new feature that introduces per-individual assessment must trigger a new classification assessment before development begins | Ongoing — embedded in product governance |
| **G4 — Post-market monitoring plan** | As provider under Article 72 of the EU AI Act, the aggregator is required to have an active post-market monitoring system once TermsIQ is live. This is currently absent from the compliance documentation. Post-market monitoring means: tracking extraction accuracy over time, monitoring confidence score drift, logging human review overrides, and having a defined process for reporting serious incidents to the national market surveillance authority if incorrect data causes consumer harm. | Define and document a post-market monitoring plan before go-live, covering: (1) monthly accuracy spot-checks against source documents; (2) confidence score trend monitoring with alert thresholds; (3) human review override rate tracking; (4) incident classification criteria and national authority reporting procedure. LangSmith already provides the per-run tracing infrastructure — the monitoring plan formalises what to do with that data. | Before production go-live |
| **G5 — Legal review of web scraping and IP position** | TermsIQ's ingestion pipeline fetches supplier documents directly from supplier websites in some cases (web crawl route), which raises two distinct legal questions neither of which has been through external legal review yet: (1) whether automated access is permitted under each supplier site's own Terms of Use, separate from any EU AI Act or GDPR question; (2) whether extracting structured factual fields from a copyrighted document constitutes reproduction of that copyright, separate from any personal-data question. This is not a data protection matter — it sits under contract and IP law, and is tracked here, and in the risk register as R3 and R11, rather than in the GDPR documentation. | External legal review scoped specifically to web scraping permissibility and IP/copyright position (already budgeted — see ROI document, €3,000–8,000, one-off). See Section 3.5 below for the internal position pending that review. | Before any web-crawl ingestion route goes live; direct supplier document feeds (SFTP/email) are the default and unaffected by this gap |

---

### 3.5 Legal basis for supplier document processing — web scraping and IP position

This section documents TermsIQ's internal legal position on two questions ahead of the external legal review tracked as Gap G5. It is not a substitute for that review — it is the working basis the system was designed against, so that the eventual review has something concrete to confirm, adjust, or overturn.

**Is automated access to a supplier's website permitted?**

This is a contract-law question, not a data-protection one — it turns on each supplier website's own Terms of Use, not on GDPR or the EU AI Act. TermsIQ's design treats this as a per-supplier question rather than a blanket assumption:

- **Direct document feed (SFTP, email, or supplier-provided API) is the default ingestion route**, used wherever a supplier relationship exists. This sidesteps the question entirely — there is no scraping to assess if the supplier is providing the document directly.
- **Web crawling is a fallback route only**, used where no direct feed exists, and only after a per-supplier check of that site's Terms of Use for anti-scraping clauses.
- Where a supplier's Terms of Use explicitly prohibit automated access, the web-crawl route for that supplier is blocked and the supplier communication programme is used to request a direct feed instead.
- This is the same logic documented as **R3** in the risk register: the mitigation is "default to direct document feed... use web crawling only as a fallback and only after legal sign-off per supplier."

**Does extracting structured fields from a supplier's document infringe their copyright?**

The working position, pending formal legal confirmation, rests on a distinction copyright law generally draws between an idea and its expression:

- **Copyright protects the expression of a document — its specific wording, structure, and layout — not the underlying facts it states.** A pickup grace period of "60 minutes" is a fact; the sentence that states it is the supplier's expression.
- TermsIQ's pipeline extracts and restates facts in a structured format (`grace_period_minutes: 60`) — it does not reproduce the supplier's original sentence as the API output.
- The one place verbatim text appears is `source_text` — a short quote (enforced under 80 characters in the extraction prompt) used solely for human verification, not displayed to end consumers as a substitute for the source document. This is a deliberate design constraint, not just a UX choice: short, attributed quotes used for verification sit closer to established fair-use/fair-dealing territory than reproducing a document's substantive content would.
- This is the same logic documented as **R11** in the risk register, rated **Low** likelihood and impact, with the same mitigation: legal review before go-live, and a preference for obtaining explicit supplier consent for T&C data feeds through the supplier communication programme — which, if achieved, would moot the copyright question entirely for that supplier.

**Why this sits here and not in the GDPR documentation**

GDPR and the EU AI Act both govern *how personal data and AI systems are regulated*. Web scraping permissibility and copyright are a different body of law — contract law and intellectual property law — that happen to apply to the same pipeline. Cross-referenced from the risk register (R3, R11) and the Technical Documentation outline (Section 10.3 below), this section is the substantive write-up; the other references point back here rather than duplicating it.

---

## Section 4 — Technical Documentation Outline

The following table of contents represents the full technical documentation package that would be required if TermsIQ were reclassified as High Risk, or that is recommended as good practice for a production Limited Risk system. Items marked *(MVP)* are recommended for completion before go-live regardless of risk class.

---

### TermsIQ — Technical Documentation Package
**Table of Contents**

**1. System Overview**
- 1.1 System name, version, and operator details
- 1.2 System purpose and intended use
- 1.3 Intended users and deployment context
- 1.4 Geographic scope and operational markets
- 1.5 Out-of-scope uses

**2. System Architecture**
- 2.1 High-level architecture diagram *(MVP)*
- 2.2 Pipeline stage descriptions (Ingest → Extract → Validate → Store → Serve)
- 2.3 LLM provider integration (OpenAI GPT-4o-mini via Azure Germany North)
- 2.4 Infrastructure stack (FastAPI, PostgreSQL, Qdrant, cloud provider, region)
- 2.6 API response schema and field definitions

**3. AI Model Information**
- 3.1 Models used (GPT-4o-mini) and provider details
- 3.2 GPAI model cards / provider documentation references
- 3.3 Prompt design and extraction schema (system prompt, field definitions, few-shot examples)
- 3.4 Confidence scoring methodology

**4. Data Documentation**
- 4.1 Input data sources (supplier PDFs, Excel, XML, web pages)
- 4.2 Reference data sources (COB Minimum Amount of Coverage 2026)
- 4.3 Data residency and storage locations *(MVP)*
- 4.4 Data retention policy
- 4.5 Version history and audit trail design *(MVP)*
- 4.6 GDPR data flow map (cross-reference: gdpr_documentation.md)

**5. Performance and Accuracy**
- 5.1 Accuracy targets and measurement methodology *(MVP)*
- 5.2 Ground-truth validation set design and composition
- 5.3 Baseline accuracy results (pre-production testing)
- 5.4 Ongoing accuracy monitoring plan
- 5.5 Known limitations and edge cases (e.g. Austria TPL, France "unlimited", handwritten documents)

**6. Human Oversight**
- 6.1 Human review queue design and workflow *(MVP)*
- 6.2 Confidence threshold policy (thresholds, fallback behaviour)
- 6.3 Escalation procedure for ambiguous or contested extractions
- 6.4 Content team role definition (data governance vs data entry)
- 6.5 Override and correction procedure

**7. Change Detection and Monitoring**
- 7.1 Document change detection methodology (hash comparison, diff extraction)
- 7.2 Alert and notification workflow
- 7.3 COB document monitoring schedule
- 7.4 API performance monitoring (latency, availability, error rates)
- 7.5 Extraction anomaly detection (confidence score drift, volume spikes)

**8. Risk Management**
- 8.1 EU AI Act risk classification (cross-reference: this document) *(MVP)*
- 8.2 Risk register (cross-reference: roi_risk_assessment.md)
- 8.3 Incident response procedure
- 8.4 Supplier document ingestion security controls
- 8.5 API access controls and key management

**9. Transparency and Disclosure**
- 9.1 API response metadata specification *(MVP)*
- 9.2 Confidence score and source attribution documentation
- 9.3 OTA partner transparency guidance
- 9.4 COB disclaimer language for API responses

**10. Legal and Compliance**
- 10.1 EU AI Act classification assessment (cross-reference: this document) *(MVP)*
- 10.2 GDPR documentation (cross-reference: gdpr_documentation.md) *(MVP)*
- 10.3 Legal basis for supplier document processing (IP, web scraping, copyright) — see Section 3.5 *(MVP)*
- 10.4 OTA partner contract clauses (T&C data accuracy, AI disclosure)
- 10.5 EU AI Act scope change monitoring procedure

**11. Deployment and Maintenance**
- 11.1 Deployment plan (shadow mode → pilot → production)
- 11.2 Rollback procedure
- 11.3 Model/prompt maintenance schedule
- 11.4 Supplier ingestion handler maintenance
- 11.5 Decommissioning plan

**12. Change Log**
- Version history of this documentation package

---

*TermsIQ — EU AI Act Compliance Documentation*
*Document version 1.3 — June 2026*
*Classification: Limited Risk — Article 50 EU AI Act*
*Provider: Aggregator (Article 3(3)) | Deployer: OTA partners (Article 3(4))*
*Next review: June 2027 or upon material scope change*
