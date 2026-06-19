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
                                    - OpenAI GPT-4o (Azure Germany North)
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
| **What data** | Supplier T&C document content (text) sent to OpenAI GPT-4o (Azure Germany North) for extraction. Not personal data — supplier commercial documents only. |
| **Purpose** | Extract structured T&C fields from unstructured documents using large language models |
| **Legal basis** | **Not applicable** — no personal data is sent to external LLM APIs. Only supplier commercial document text is processed. |
| **Retention period** | Not retained by pipeline — API call is stateless. Provider data retention governed by provider terms (see Section 5). |
| **Third-party recipients** | OpenAI (via Azure Germany North) |
| **Data location** | Germany (Azure Germany North — contractually guaranteed) |
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

This activity is selected for DPIA because it involves sending document content to an external third-party provider (OpenAI via Azure Germany North) outside the aggregator's direct control, creating a residual risk of unintended data exposure if personal data were inadvertently present in a supplier document.

---

### 3.1 Description of the processing

TermsIQ sends the text content of supplier T&C documents to the OpenAI GPT-4o API (via Azure Germany North) to extract structured field values. The documents are supplier commercial terms — they are not intended to contain personal data. However, there is a residual risk that supplier documents could inadvertently contain personal data (e.g. a named contact, a specific customer example cited in the terms).

The LLM API call is stateless: the document text is sent, the structured extraction is returned, and no data is retained in the pipeline from that call beyond the extracted fields. However, OpenAI may temporarily process the input text according to its data processing terms — mitigated by using the zero-data-retention (ZDR) Azure OpenAI Enterprise API tier.

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
| Personal data inadvertently present in a supplier document is sent to OpenAI API | Very low (supplier T&C documents are not personal data by design) | Medium (data subject unaware; no consent) | **Low** |
| LLM provider uses submitted document content for model training | Very low (Azure OpenAI Enterprise API ZDR terms contractually exclude training on API inputs) | High (if it occurred, personal data could be embedded in model weights) | **Very Low** |
| Data routed outside Germany in violation of data residency requirement | Low (Azure Germany North contractually restricts processing to Germany) | High (regulatory violation; GDPR Art. 46 breach) | **Low** |
| Incorrect AI extraction displayed to end customer at booking (wrong payment rule, wrong licence rule, wrong grace period) | Medium (LLM hallucination is a known risk; confidence scoring and human review reduce but do not eliminate it) | High (customer acts on incorrect information, arrives at counter, booking refused — no recourse; potential regulatory complaint under EU consumer law) | **Medium** |
| Unauthorised access to documents in transit | Very low (TLS in transit; API key authentication) | High | **Low** |

---

### 3.4 Mitigation measures

| Risk | Mitigation |
|---|---|
| Inadvertent personal data in supplier document | Pre-processing step scans documents for personal data patterns (names, email addresses, ID numbers) before API submission. If detected, document is routed to human review before LLM processing. |
| LLM provider training on inputs | Azure OpenAI Enterprise API ZDR tier used — contractual zero-data-retention; inputs excluded from model training. Confirm ZDR is enabled on the Azure subscription before go-live and document in the vendor agreement. |
| Data residency violation | Azure OpenAI Germany North — contractual Germany-region processing guaranteed. No other LLM provider in the pipeline. If Azure OpenAI experiences an outage, the nightly batch retries the following night — T&C documents do not change daily, so a one-night delay is operationally acceptable. |
| Incorrect AI extraction displayed to end customer | Confidence threshold + mandatory human review gate — no extraction goes live in the API without validation.  fallback below minimum confidence threshold. Source, confidence score, and extracted_at date included in every API response. Nightly batch means errors are caught before reaching any customer. |
| Data in transit | TLS 1.3 enforced for all API calls. API keys stored in secrets manager, never in code. |
| Scope creep (future personal data inclusion) | Any pipeline extension that would introduce personal data (e.g. driver nationality for licence validation per booking) requires a new DPIA before development. Embedded in product governance policy. **Highest-risk future scenario:** if an OTA partner begins sending customer booking data (driver name, nationality, licence number) alongside a T&C API query — for example to get a per-booking licence acceptance prediction — this would immediately trigger a full DPIA and likely a High Risk reclassification under Annex III. This scenario must be explicitly prohibited in the current API contract until a proper impact assessment is completed. |

---

### 3.5 Residual risk rating

| | |
|---|---|
| **Residual risk after mitigations** | **Low** |
| **Rationale** | The core processing involves no personal data. The residual risks (inadvertent exposure in supplier documents; incorrect extraction displayed to end customer) are mitigated by contractual ZDR controls, pre-processing, and the human review gate. Single-provider architecture with Azure Germany North eliminates data residency uncertainty. |
| **Independent review required?** | Yes — before production go-live, a qualified independent reviewer (see Section 3.6) should review this DPIA and confirm the residual risk rating |
| **Review trigger** | Any pipeline change that introduces personal data; any change of LLM provider; annual review |

---

### 3.6 DPO status — exemption analysis

GDPR Article 37 makes DPO appointment mandatory in three scenarios: (1) the organisation is a public authority; (2) core activities require regular, systematic, large-scale monitoring of individuals; (3) core activities involve large-scale processing of special category data (Art. 9) or criminal-records data (Art. 10).

**TermsIQ's assessment against each trigger:**

| Trigger | Applies to TermsIQ? | Rationale |
|---|---|---|
| Public authority or body | No | TermsIQ is operated by a private commercial aggregator |
| Large-scale systematic monitoring of individuals | No | TermsIQ monitors supplier *documents* for changes — not the behaviour, location, or activity of natural persons. This is categorically different from the monitoring Article 37 targets (e.g. behavioural advertising, location tracking) |
| Large-scale special category data processing | No | TermsIQ processes commercial T&C field values (TPL amounts, grace periods, licence rules) — none of which are special category data under Art. 9 or Art. 10 |

**Conclusion: a formally designated DPO is not legally mandatory for TermsIQ under Article 37**, in either the vendor's role as controller (for the OpenAI relationship) or as processor (for the client relationship). This exemption analysis should be retained as a standing document — regulators increasingly expect organisations to show their reasoning for *not* appointing a DPO, not just silence on the question.

**What replaces a formal DPO in practice:**

- **A documented exemption analysis** (this section) — reviewed annually or on any material scope change
- **A qualified independent reviewer** for the DPIA before go-live — this can be the external legal/compliance counsel already budgeted in the project's compliance line items; it does not require a permanently appointed DPO
- **A named internal point of contact** for data protection matters — informal, but someone accountable must be named even without the formal title

If TermsIQ's scope expands to include customer or driver personal data (see the scope-creep flag in Section 3.4), this exemption analysis must be revisited — that kind of expansion could plausibly trigger the large-scale monitoring threshold and make a formal DPO appointment necessary.

**Two separate DPA relationships, not one:**

Because the vendor sits between OpenAI and the client, there are two distinct Data Processing Agreements, with the vendor playing a different role in each:

| Relationship | Vendor's role | Counterparty's role | What it covers |
|---|---|---|---|
| Vendor ↔ OpenAI (via Azure) | **Controller** | OpenAI = **Processor** | Vendor decides to send document text to OpenAI for extraction; OpenAI processes it on the vendor's behalf, under ZDR terms, Germany North region |
| Vendor ↔ Client (OTA/aggregator) | **Processor** | Client = **Controller** | Client engages the vendor to process data on their behalf (currently minimal, since no customer data is in scope); must explicitly disclose OpenAI as a sub-processor |

The client never contracts directly with OpenAI — they have no relationship with it at all. Their only data-protection relationship is with the vendor. The vendor's DPA with the client should explicitly name OpenAI as a sub-processor and confirm Germany-region processing throughout, so the client's own DPO (if they have one — most OTAs of meaningful size already do, for reasons unrelated to TermsIQ) can complete their own review quickly.

---

## Section 4 — Data Subject Rights

TermsIQ processes minimal personal data (content team staff, supplier contacts, API request logs). The following table sets out how each right under GDPR Chapter III is addressed. As established in Section 3.6, TermsIQ is not required to appoint a formally designated DPO — rights requests below are handled by the named internal data protection point of contact.

| Right | Applicable to TermsIQ? | How it is addressed |
|---|---|---|
| **Right of access (Art. 15)** | Yes — content team staff and supplier contacts can request access to their personal data | Requests directed to the internal data protection point of contact. Content team data held in the review interface database; supplier contact data in the supplier record. Both are exportable within 30 days of request. |
| **Right to rectification (Art. 16)** | Yes — incorrect personal data (e.g. wrong name, wrong email) can be corrected | Data protection point of contact processes correction requests. Data updated in the relevant system within 30 days. Audit trail entries that include reviewer ID are not deleted but a correction note is appended. |
| **Right to erasure (Art. 17)** | Partial — audit trail entries containing reviewer IDs cannot be erased while the retention period applies (regulatory obligation), but other personal data can be erased on request | Login accounts and supplier contacts can be deleted on request. Audit trail reviewer IDs are pseudonymised (replaced with a role reference) where erasure is requested during the retention period. |
| **Right to restriction (Art. 18)** | Yes | Processing can be restricted pending resolution of accuracy disputes. Restricted accounts are flagged in the review interface. |
| **Right to data portability (Art. 20)** | Yes — for content team staff and supplier contacts where processing is based on contract | Data exported in machine-readable format (CSV/JSON) within 30 days of request. |
| **Right to object (Art. 21)** | Yes — for processing based on legitimate interest | Objections assessed by the data protection point of contact, with external legal counsel consulted where needed. If legitimate interest is overridden by the data subject's interests, processing ceases. |
| **Rights related to automated decision-making (Art. 22)** | Not applicable | TermsIQ does not make automated decisions about individuals. The confidence scoring system flags extractions for human review — it does not make decisions about natural persons. |

**How to exercise rights:** Data subjects should contact the internal data protection point of contact at [contact to be defined before go-live]. Requests are acknowledged within 72 hours and fulfilled within 30 days (extendable by 2 months for complex requests with notification).

---

## Section 5 — Third-Party Data Transfers

### 5.1 OpenAI (via Azure OpenAI Service)

| Attribute | Detail |
|---|---|
| **Service** | OpenAI GPT-4o via Azure OpenAI Service |
| **Roles** | Vendor = **Controller**; OpenAI/Azure = **Processor**. The vendor decides what data is sent and why; OpenAI processes it on the vendor's behalf under the terms below. |
| **What data is sent** | Supplier T&C document text (not personal data in normal operation) |
| **Purpose** | LLM-based T&C field extraction (primary provider) |
| **Legal transfer mechanism** | Standard Contractual Clauses (SCCs) not required — Azure OpenAI Germany North processes data within Germany/EU. Processing governed by Microsoft Azure Data Processing Agreement with EU GDPR terms. |
| **Data storage location** | Germany North (Azure region) — contractually guaranteed |
| **Provider training on inputs** | No — Azure OpenAI Enterprise API terms exclude customer data from model training |
| **Retention by provider** | Per Azure OpenAI terms: API inputs and outputs not retained beyond the API call by default (zero-data-retention available) |
| **Sub-processor disclosure to client** | Because the vendor acts as processor for the client (see Section 5.4), OpenAI/Azure must be explicitly disclosed to the client as a sub-processor in the vendor-client DPA, including the Germany North region commitment and ZDR terms. |
| **Action required** | Confirm ZDR terms are enabled on the Azure OpenAI subscription before go-live. Obtain and store a copy of the Azure DPA — this is the vendor's own DPA, signed by the vendor as controller, separate from the vendor-client DPA in Section 5.4. |

---

### 5.2 Cloud infrastructure provider (Germany region)

| Attribute | Detail |
|---|---|
| **Service** | AWS Frankfurt / Azure Germany North (or equivalent Germany-region cloud provider) |
| **What data is stored** | All TermsIQ data: supplier documents, extracted T&C knowledge base, audit trail, content team user accounts, API logs |
| **Purpose** | Infrastructure hosting for the entire TermsIQ pipeline |
| **Legal transfer mechanism** | No international transfer — Germany-region processing within EU. Governed by provider's EU DPA (AWS DPA / Microsoft Azure DPA). |
| **Data storage location** | Germany |
| **Action required** | Confirm Germany-region data residency is contractually locked in hosting agreement. Document provider DPA reference. |

---

### 5.3 Council of Bureaux (COB) — reference data only

| Attribute | Detail |
|---|---|
| **Service** | cobx.org — COB Minimum Amount of Coverage reference document |
| **What data is accessed** | Statutory minimum TPL amounts by country — public reference data. No personal data. |
| **Purpose** | Cross-reference for TPL field resolution |
| **Legal transfer mechanism** | Not applicable — publicly available reference document, no personal data involved |
| **Action required** | None from a GDPR perspective. Maintain COB disclaimer in API responses per COB terms of use. |

---

### 5.4 Vendor ↔ Client DPA (vendor as processor)

This is a separate agreement from Section 5.1 — here, the vendor is the **processor**, not the controller, and the client (the OTA/aggregator buying TermsIQ) is the **controller**. This DPA must be in place before the client's data (currently minimal — see Preliminary Note) is processed under the commercial relationship.

| Required clause | What it should state |
|---|---|
| **Subject matter and duration** | Processing is limited to supplier T&C documents for the contract term; explicitly excludes customer/booking personal data unless a future amendment is signed |
| **Nature and purpose** | Extraction of structured T&C fields for API delivery to the client |
| **Type of data and data subjects** | Currently none, or minimal (supplier contact details only) — stated explicitly so scope creep requires a contract amendment, not a silent expansion |
| **Sub-processor disclosure** | OpenAI/Azure OpenAI Service (Germany North, ZDR terms) must be named explicitly — see Section 5.1. The client has the right to be informed of any new sub-processor before it is engaged. |
| **Security measures** | TLS 1.3 in transit, Germany-region encryption at rest, access controls, the audit trail and confidence-scoring system already built into the pipeline |
| **Data subject rights support** | Vendor commits to supporting the client in fulfilling any data subject request within the statutory timeframe, per Section 4 |
| **Breach notification** | Vendor notifies the client promptly (target: within 24–72 hours of becoming aware) of any breach involving the client's data |
| **Audit rights** | Client may request evidence of compliance, including this DPIA, the Azure DPA, and relevant certifications |
| **Deletion/return at contract end** | What happens to any client-related data the vendor holds when the relationship ends |
| **International transfer safeguards** | Confirms all processing — vendor infrastructure and the OpenAI sub-processor — stays within Germany/EU, avoiding the need for Standard Contractual Clauses |

**Action required:** Draft and execute this DPA with each client before go-live, alongside the OTA partner transparency clause (Gap G1 in the EU AI Act compliance documentation).

---

## Section 6 — Data Governance Summary

| Control | Status | Owner |
|---|---|---|
| Privacy by design embedded in pipeline architecture | ✅ | Head of Engineering |
| Data minimisation — only document text sent to LLM (no booking or customer data) | ✅ | Head of Engineering |
| Germany-region data residency enforced for primary infrastructure | ✅ | Head of Engineering |
| DPIA completed for highest-risk processing activity | ✅ This document | Internal data protection point of contact |
| DPO exemption analysis documented (Art. 37 not triggered) | ✅ This document, Section 3.6 | Internal data protection point of contact |
| Independent qualified review of DPIA before go-live | ⚠️ Pending | External legal/compliance counsel |
| Data subject rights procedure documented | ✅ This document | Internal data protection point of contact |
| Vendor's own DPA with OpenAI/Azure (vendor as controller) | ⚠️ In progress | Legal |
| Vendor-client DPA (vendor as processor, Section 5.4) | ⚠️ To be drafted per client | Legal |
| Retention schedules implemented in system | ⚠️ To be built | Head of Engineering |
| Personal data pre-scan before LLM submission | ⚠️ To be built | Head of Engineering |
| Annual GDPR review scheduled | ⚠️ To be scheduled | Internal data protection point of contact |

---

*TermsIQ — GDPR Documentation*
*Document version 1.3 — June 2026*
*Data Controller (for client-relationship data): [Aggregator legal entity name — to be completed]*
*Data Controller (for OpenAI relationship): Vendor*
*Formally designated DPO: Not legally required (see Section 3.6) — internal data protection point of contact: [name and contact to be completed before go-live]*
