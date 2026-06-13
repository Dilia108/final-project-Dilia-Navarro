# TermsIQ — GDPR Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.0 — June 2026

---

## Preliminary Note — Personal Data Assessment

The most important finding in this document: **TermsIQ v1 does not process personal data as its primary function.** The system processes supplier commercial documents — PDFs, Excel files, web pages, XML feeds — containing business terms and conditions. These are not personal data under GDPR Article 4(1).

However, three categories of data warrant careful assessment:

| Data category | Personal data? | Rationale |
|---|---|---|
| Supplier T&C documents (PDFs, web pages) | ❌ No | Commercial documents describing supplier policies — no natural persons identified |
| COB reference data | ❌ No | Statutory minimum insurance amounts by country — no individuals |
| API logs (request metadata) | ⚠️ Potentially | IP addresses of OTA API callers may constitute personal data if they identify individuals |
| Content team user accounts | ✅ Yes | Names, email addresses, login activity of internal staff using the review interface |
| Supplier contact details | ✅ Yes | Names and email addresses of supplier account managers who communicate T&C updates |

This document addresses all five categories. The personal data categories (content team users and supplier contacts) are incidental to the core system function but require proper governance.

---

## Section 1 — Data Flow Map

### 1.1 Overview

```
EXTERNAL SOURCES                    TERMSIQ PIPELINE                    OUTPUTS
─────────────────                   ────────────────                    ───────

Supplier websites ──────────────►  [1] INGEST                         
Supplier PDFs (email/SFTP) ──────►  - Document hash & store  ────────► Document store
Supplier Excel/XML ──────────────►  - OCR if scanned                   (Germany, encrypted)
                                    - Version stamp
                                         │
                                         ▼
COB reference (cobx.org) ──────────► [2] EXTRACT
                                    - OpenAI GPT-4o (primary)
                                    - Anthropic Claude (fallback)
                                    - Structured JSON output
                                         │
                                         ▼
Content team ◄─────────────────── [3] VALIDATE
(human review queue)                - Schema validation
     │                              - Confidence scoring
     │ approved                     - Flag for human review
     ▼
                                   [4] STORE & VERSION ────────────────► T&C knowledge base
                                    - Keyed: supplier × country × field  (Germany, PostgreSQL)
                                    - Full version history
                                    - Audit trail
                                         │
                                         ▼
OTA partners ◄────────────────── [5] SERVE & MONITOR
(API consumers)                     - Append to API response
                                    - Confidence + source metadata
                                    - Daily change detection
                                         │
                                         ▼
                                   [6] MONITORING LOGS ───────────────► Log store
                                    - API request logs                   (Germany, 90-day retention)
                                    - Extraction accuracy logs
                                    - Change detection alerts
```

### 1.2 Personal data flows specifically

```
Content team staff
  ├── Name + email → stored in review interface user database (Germany)
  ├── Login activity → access logs (Germany, 90-day retention)
  └── Review decisions → audit trail (Germany, retained with extraction version)

Supplier contacts
  ├── Name + email → stored in supplier contact record (Germany)
  ├── Email correspondence → referenced in document provenance log
  └── Not shared with any third party
  
API request logs
  ├── OTA caller IP address → request log (Germany)
  ├── Timestamp + endpoint called → request log
  └── Retained 90 days, then deleted
```

---

## Section 2 — Processing Activities Register

### 2.1 Processing activity 1 — Supplier document ingestion and storage

| Attribute | Detail |
|---|---|
| **What data** | Supplier commercial T&C documents (PDFs, Excel, XML, web pages). Not personal data. Supplier contact name and email where documents are received via email from account managers (personal data — incidental). |
| **Purpose** | Store source documents for extraction, versioning, audit trail, and change detection |
| **Legal basis** | **Legitimate interest** (Art. 6(1)(f)) — processing supplier contact details is necessary for the legitimate interest of maintaining accurate sourcing records and contact provenance for the T&C data pipeline. Supplier contacts are business representatives; their professional contact details are processed in a B2B context. |
| **Retention period** | Documents retained for the lifetime of the supplier relationship + 3 years (audit trail requirement). Supplier contact details retained while the supplier is active + 1 year. |
| **Third-party recipients** | None — documents stored in Germany-region infrastructure only |
| **Data location** | Germany (AWS Frankfurt or equivalent) |

---

### 2.2 Processing activity 2 — LLM extraction via external API

| Attribute | Detail |
|---|---|
| **What data** | Supplier T&C document content (text) sent to OpenAI GPT-4o or Anthropic Claude API for extraction. Not personal data — supplier commercial documents only. |
| **Purpose** | Extract structured T&C fields from unstructured documents using large language models |
| **Legal basis** | **Not applicable** — no personal data is sent to external LLM APIs. Only supplier commercial document text is processed. |
| **Retention period** | Not retained by pipeline — API call is stateless. Provider data retention governed by provider terms (see Section 5). |
| **Third-party recipients** | OpenAI (via Azure Germany North); Anthropic (fallback, data residency under legal review) |
| **Data location** | Germany (Azure Germany North for OpenAI); Anthropic location under review |
| **Note** | Before any pipeline extension that would send personal data to an external LLM API, a new DPIA must be completed and appropriate safeguards established. |

---

### 2.3 Processing activity 3 — T&C knowledge base storage and versioning

| Attribute | Detail |
|---|---|
| **What data** | Extracted T&C field values (TPL amounts, grace periods, licence rules, payment rules, cross-border conditions) keyed by supplier × pickup country × rule type. Not personal data. Extraction metadata: source document URL, extracted\_at timestamp, confidence score, reviewer ID (content team member — personal data). |
| **Purpose** | Store structured T&C data for API serving; maintain full version history for audit trail and regulatory compliance |
| **Legal basis** | **Legitimate interest** (Art. 6(1)(f)) for reviewer ID — necessary to maintain an audit trail of who reviewed and approved each extraction. **Legal obligation** (Art. 6(1)(c)) — audit trail is required for EU consumer law compliance and EU AI Act transparency obligations. |
| **Retention period** | T&C field values: retained for the lifetime of the supplier relationship + 5 years (regulatory audit trail). Reviewer ID in audit trail: retained with the extraction record (same period). |
| **Third-party recipients** | None — knowledge base is internal only |
| **Data location** | Germany (PostgreSQL, Germany-region hosting) |

---

### 2.4 Processing activity 4 — API serving to OTA partners

| Attribute | Detail |
|---|---|
| **What data** | Structured T&C field values + metadata (source, confidence, timestamp) served via API response. Not personal data. API request logs: caller IP address, timestamp, endpoint, response code (potentially personal data if IP identifies an individual). |
| **Purpose** | Serve structured T&C data to OTA booking channel partners for display to consumers |
| **Legal basis** | **Contract** (Art. 6(1)(b)) — API access is governed by a contract between the aggregator and each OTA partner. Request logging: **legitimate interest** (Art. 6(1)(f)) — necessary for security monitoring, abuse prevention, and system performance management. |
| **Retention period** | API response data: not stored (stateless). Request logs: 90 days, then deleted automatically. |
| **Third-party recipients** | OTA partners receive T&C field data only — no personal data of individuals is shared with OTAs via this pipeline |
| **Data location** | Germany (API hosted Germany-region; request logs Germany-region) |

---

### 2.5 Processing activity 5 — Content team user accounts and review interface

| Attribute | Detail |
|---|---|
| **What data** | Content team member names, email addresses, login credentials (hashed), login timestamps, review decisions and comments linked to specific extraction records |
| **Purpose** | Authenticate authorised reviewers; maintain audit trail of human review decisions; manage access to the validation interface |
| **Legal basis** | **Contract** (Art. 6(1)(b)) — processing is necessary for the performance of the employment or contractor relationship. **Legal obligation** (Art. 6(1)(c)) — audit trail of human review decisions is required for EU AI Act human oversight documentation. |
| **Retention period** | Active accounts: duration of employment/contract + 1 year. Audit trail entries: retained with the extraction record (5 years — see 2.3). Login logs: 90 days. |
| **Third-party recipients** | None |
| **Data location** | Germany |

---

## Section 3 — Data Protection Impact Assessment (DPIA)

### Highest-risk processing activity: LLM extraction via external API (Activity 2.2)

This activity is selected for DPIA because it involves sending document content to external third-party providers (OpenAI, Anthropic) outside the aggregator's direct control, creating the highest risk of unintended data exposure if personal data were inadvertently present in a supplier document.

---

### 3.1 Description of the processing

TermsIQ sends the text content of supplier T&C documents to external LLM APIs (OpenAI GPT-4o via Azure, Anthropic Claude as fallback) to extract structured field values. The documents are supplier commercial terms — they are not intended to contain personal data. However, there is a residual risk that supplier documents could inadvertently contain personal data (e.g. a named contact, a specific customer example cited in the terms).

The LLM API call is stateless: the document text is sent, the structured extraction is returned, and no data is retained in the pipeline from that call beyond the extracted fields. However, the LLM provider may process and temporarily store the input text according to its own data processing terms.

**Scope:** Approximately 500–25,000 document ingestions at MVP to scale, plus ongoing updates (~50–2,500/month). All documents are supplier commercial terms. No customer or driver personal data is intentionally included.

---

### 3.2 Necessity and proportionality assessment

| Question | Assessment |
|---|---|
| **Is the processing necessary?** | Yes — LLM extraction is the core technical mechanism. No alternative technology achieves the same accuracy across multi-language, multi-format supplier documents at the required scale. |
| **Is it proportionate to the purpose?** | Yes — only the document text required for extraction is sent. Documents are pre-processed to strip headers, footers, and non-T&C content before API submission, reducing token count and limiting exposure. |
| **Could the purpose be achieved with less data?** | Partially — pre-processing reduces volume. A fully self-hosted open-weight model (e.g. Mistral) would eliminate third-party exposure entirely but introduces accuracy trade-offs and infrastructure cost. This is flagged as a future option. |
| **Is personal data actually present?** | Almost certainly not in normal operation — supplier T&C documents are commercial policy documents. The risk is residual (inadvertent inclusion). |

---

### 3.3 Risks to data subjects

| Risk | Likelihood | Severity | Risk level |
|---|---|---|---|
| Personal data inadvertently present in a supplier document is sent to an external LLM provider | Very low (supplier T&C documents are not personal data by design) | Medium (data subject unaware; no consent) | **Low** |
| LLM provider uses submitted document content for model training | Low (both OpenAI and Anthropic offer API terms that exclude training on API inputs by default) | High (if it occurred, personal data could be embedded in model weights) | **Low–Medium** |
| Data routed outside Germany in violation of data residency requirement | Low (Azure Germany North contractually restricts processing to Germany; Anthropic under review) | High (regulatory violation; GDPR Art. 46 breach) | **Low–Medium** |
| Unauthorised access to documents in transit | Very low (TLS in transit; API key authentication) | High | **Low** |

---

### 3.4 Mitigation measures

| Risk | Mitigation |
|---|---|
| Inadvertent personal data in supplier document | Pre-processing step scans documents for personal data patterns (names, email addresses, ID numbers) before API submission. If detected, document is routed to human review before LLM processing. |
| LLM provider training on inputs | Use API tiers with contractual zero-data-retention (ZDR) terms: OpenAI Enterprise API / Azure OpenAI (no training on inputs); Anthropic API (no training on API inputs by default). Confirm and document in vendor agreements. |
| Data residency violation | Azure OpenAI Germany North used as primary — contractual Germany-region processing. Anthropic fallback: legal review of DPA required before enabling in production; if unresolvable, replace with EU-hosted open-weight model. |
| Data in transit | TLS 1.3 enforced for all API calls. API keys stored in secrets manager, never in code. |
| Scope creep (future personal data inclusion) | Any pipeline extension that would introduce personal data (e.g. driver nationality for licence validation per booking) requires a new DPIA before development. Embedded in product governance policy. |

---

### 3.5 Residual risk rating

| | |
|---|---|
| **Residual risk after mitigations** | **Low** |
| **Rationale** | The core processing involves no personal data. The residual risks (inadvertent exposure, provider training) are mitigated by contractual controls and pre-processing. The data residency gap (Anthropic) is a known issue with a defined resolution path. |
| **DPO sign-off required?** | Yes — before production go-live, the DPO should review this DPIA and confirm the residual risk rating |
| **Review trigger** | Any pipeline change that introduces personal data; any change of LLM provider; annual review |

---

## Section 4 — Data Subject Rights

TermsIQ processes minimal personal data (content team staff, supplier contacts, API request logs). The following table sets out how each right under GDPR Chapter III is addressed.

| Right | Applicable to TermsIQ? | How it is addressed |
|---|---|---|
| **Right of access (Art. 15)** | Yes — content team staff and supplier contacts can request access to their personal data | Requests directed to the Data Protection Officer. Content team data held in the review interface database; supplier contact data in the supplier record. Both are exportable within 30 days of request. |
| **Right to rectification (Art. 16)** | Yes — incorrect personal data (e.g. wrong name, wrong email) can be corrected | DPO processes correction requests. Data updated in the relevant system within 30 days. Audit trail entries that include reviewer ID are not deleted but a correction note is appended. |
| **Right to erasure (Art. 17)** | Partial — audit trail entries containing reviewer IDs cannot be erased while the retention period applies (regulatory obligation), but other personal data can be erased on request | Login accounts and supplier contacts can be deleted on request. Audit trail reviewer IDs are pseudonymised (replaced with a role reference) where erasure is requested during the retention period. |
| **Right to restriction (Art. 18)** | Yes | Processing can be restricted pending resolution of accuracy disputes. Restricted accounts are flagged in the review interface. |
| **Right to data portability (Art. 20)** | Yes — for content team staff and supplier contacts where processing is based on contract | Data exported in machine-readable format (CSV/JSON) within 30 days of request. |
| **Right to object (Art. 21)** | Yes — for processing based on legitimate interest | Objections assessed by the DPO. If legitimate interest is overridden by the data subject's interests, processing ceases. |
| **Rights related to automated decision-making (Art. 22)** | Not applicable | TermsIQ does not make automated decisions about individuals. The confidence scoring system flags extractions for human review — it does not make decisions about natural persons. |

**How to exercise rights:** Data subjects should contact the Data Protection Officer at [DPO contact to be defined before go-live]. Requests are acknowledged within 72 hours and fulfilled within 30 days (extendable by 2 months for complex requests with notification).

---

## Section 5 — Third-Party Data Transfers

### 5.1 OpenAI (via Azure OpenAI Service)

| Attribute | Detail |
|---|---|
| **Service** | OpenAI GPT-4o via Azure OpenAI Service |
| **What data is sent** | Supplier T&C document text (not personal data in normal operation) |
| **Purpose** | LLM-based T&C field extraction (primary provider) |
| **Legal transfer mechanism** | Standard Contractual Clauses (SCCs) not required — Azure OpenAI Germany North processes data within Germany/EU. Processing governed by Microsoft Azure Data Processing Agreement with EU GDPR terms. |
| **Data storage location** | Germany North (Azure region) — contractually guaranteed |
| **Provider training on inputs** | No — Azure OpenAI Enterprise API terms exclude customer data from model training |
| **Retention by provider** | Per Azure OpenAI terms: API inputs and outputs not retained beyond the API call by default (zero-data-retention available) |
| **Action required** | Confirm ZDR terms are enabled on the Azure OpenAI subscription before go-live. Obtain and store a copy of the Azure DPA. |

---

### 5.2 Anthropic (Claude API — fallback)

| Attribute | Detail |
|---|---|
| **Service** | Anthropic Claude Sonnet API |
| **What data is sent** | Supplier T&C document text (not personal data in normal operation) |
| **Purpose** | LLM-based T&C field extraction (fallback provider for low-confidence or primary-unavailable scenarios) |
| **Legal transfer mechanism** | **Under review** — Anthropic's standard API does not currently offer a contractual EU/Germany data residency guarantee equivalent to Azure OpenAI. SCCs may be required for any processing routed to Anthropic's US-based infrastructure. |
| **Data storage location** | Anthropic standard: USA. EU residency: not currently confirmed. |
| **Provider training on inputs** | No — Anthropic API terms exclude training on API inputs by default |
| **Retention by provider** | Per Anthropic terms: API inputs and outputs not retained for training; temporary processing retention applies |
| **Action required** | **Legal review required before enabling Anthropic as production fallback.** Options: (a) obtain Anthropic DPA with EU SCCs and document transfer mechanism; (b) restrict Anthropic fallback to non-document-content tasks only; (c) replace Anthropic fallback with an EU-hosted open-weight model (e.g. Mistral Large via Mistral API, EU-hosted). Resolution required before go-live. |

---

### 5.3 Cloud infrastructure provider (Germany region)

| Attribute | Detail |
|---|---|
| **Service** | AWS Frankfurt / Azure Germany North (or equivalent Germany-region cloud provider) |
| **What data is stored** | All TermsIQ data: supplier documents, extracted T&C knowledge base, audit trail, content team user accounts, API logs |
| **Purpose** | Infrastructure hosting for the entire TermsIQ pipeline |
| **Legal transfer mechanism** | No international transfer — Germany-region processing within EU. Governed by provider's EU DPA (AWS DPA / Microsoft Azure DPA). |
| **Data storage location** | Germany |
| **Action required** | Confirm Germany-region data residency is contractually locked in hosting agreement. Document provider DPA reference. |

---

### 5.4 Council of Bureaux (COB) — reference data only

| Attribute | Detail |
|---|---|
| **Service** | cobx.org — COB Minimum Amount of Coverage reference document |
| **What data is accessed** | Statutory minimum TPL amounts by country — public reference data. No personal data. |
| **Purpose** | Cross-reference for TPL field resolution |
| **Legal transfer mechanism** | Not applicable — publicly available reference document, no personal data involved |
| **Action required** | None from a GDPR perspective. Maintain COB disclaimer in API responses per COB terms of use. |

---

## Section 6 — Data Governance Summary

| Control | Status | Owner |
|---|---|---|
| Privacy by design embedded in pipeline architecture | ✅ | Head of Engineering |
| Data minimisation — only document text sent to LLM (no booking or customer data) | ✅ | Head of Engineering |
| Germany-region data residency enforced for primary infrastructure | ✅ | Head of Engineering |
| Anthropic fallback data residency resolved before go-live | ⚠️ Pending | Legal / DPO |
| DPIA completed for highest-risk processing activity | ✅ This document | DPO |
| DPO review and sign-off before go-live | ⚠️ Pending | DPO |
| Data subject rights procedure documented | ✅ This document | DPO |
| Vendor DPAs obtained (Azure) | ⚠️ In progress | Legal |
| Vendor DPAs obtained (Anthropic) | ⚠️ Pending legal review | Legal |
| Retention schedules implemented in system | ⚠️ To be built | Head of Engineering |
| Personal data pre-scan before LLM submission | ⚠️ To be built | Head of Engineering |
| Annual GDPR review scheduled | ⚠️ To be scheduled | DPO |

---

*TermsIQ — GDPR Documentation*
*Document version 1.0 — June 2026*
*Data Controller: [Aggregator legal entity name — to be completed]*
*Data Protection Officer: [DPO name and contact — to be completed before go-live]*
