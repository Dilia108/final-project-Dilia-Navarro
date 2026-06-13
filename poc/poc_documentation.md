# TermsIQ POC Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.1 — June 2026

---

## Overview

This POC demonstrates the core TermsIQ capability across **all three real-world supplier document source types**: PDF documents, website/HTML pages, and Excel files. The same extraction pipeline handles all three — the only difference is the ingestion step that converts each format into text before sending to the LLM.

For each source type the pipeline:
1. Detects and ingests the document format
2. Extracts the 5 critical T&C fields using OpenAI GPT-4o
3. Cross-checks TPL against the COB 2026 statutory minimum table
4. Scores confidence and flags for human review if needed
5. Outputs a structured JSON record ready for API serving

**Demo recording:** A screen recording of the POC running end-to-end is included separately, showing all three source types in sequence.

---

## Tools Used and Why

| Tool | Role | Why chosen |
|---|---|---|
| **n8n** | Primary workflow orchestration (exportable JSON) | Open-source, self-hostable, supports all required node types (HTTP, Code, OpenAI, email), exportable as JSON for submission |
| **Python 3** | Runnable standalone POC script | Demonstrates the same pipeline logic immediately without needing n8n installed |
| **OpenAI GPT-4o** | LLM extraction of T&C fields | Strong structured JSON output, multilingual, temperature=0 for deterministic results |
| **Anthropic Claude** | Fallback LLM (referenced in workflow) | Used when GPT-4o confidence is LOW or primary is unavailable |
| **pypdf** | PDF text extraction | Lightweight Python library; handles multi-page PDFs |
| **BeautifulSoup4** | HTML/web page parsing | Strips nav, footer, scripts; extracts clean readable content from supplier web pages |
| **openpyxl** | Excel (.xlsx) parsing | Reads all sheets, preserves row/column structure as readable text |
| **COB 2026 table** | TPL statutory minimum reference | Built-in lookup from Council of Bureaux April 2026 edition |

---

## Source Types Supported

| Source type | Format | Real-world example | How ingested |
|---|---|---|---|
| **PDF** | `.pdf` | Hertz country T&C PDFs (`RT_FULL_ES_EN.pdf`) | pypdf text extraction; fallback to raw decode |
| **Website** | HTML via URL or `.html` | Sixt rental conditions pages, Europcar web T&C | BeautifulSoup strips nav/footer/scripts; extracts body content |
| **Excel** | `.xlsx`, `.xls`, `.csv` | Supplier SFTP drops, structured T&C spreadsheets | openpyxl reads all sheets row by row into readable text |
| **XML / plain text** | `.xml`, `.txt` | Some suppliers send XML feeds or plain text | Direct UTF-8 decode |

Auto-detection from file extension; can be overridden with `--source-type` flag.

---

## What the POC Does — Step by Step

### n8n Workflow (`poc_workflow.json`)

```
[Schedule Trigger]
       │
       ▼
[Fetch Supplier Document]      ← HTTP GET (PDF URL, web page, or Excel SFTP)
       │
       ▼
[Detect & Extract Text]        ← PDF / HTML / Excel → plain text
       │
       ▼
[Pre-process & Hash]           ← Truncate, clean, MD5 hash for change detection
       │
       ▼
[OpenAI GPT-4o Extract]        ← 5 T&C fields as structured JSON
       │
       ▼
[Validate & Score]             ← Confidence scoring, validation rules
       │
       ▼
[TPL needs COB lookup?]        ← IF branch
   YES │                NO │
       ▼                   │
[COB 2026 Lookup]            │
       └────────────────────┘
                │
                ▼
[Requires human review?]
   YES │               NO │
       ▼                  ▼
[Email review queue]  [Build API Record]
                            │
                            ▼
                      [Store in KB]
```

### Python Script (`termsiq_poc.py`) — 7 Steps

**Step 1 — Ingest document**
Auto-detects source type (PDF / web / Excel / text) from extension or `--source-type` flag. Fetches from URL or loads from local file. Applies the appropriate extractor:
- PDF → pypdf page-by-page text extraction
- Web/HTML → BeautifulSoup strips chrome, extracts body content
- Excel → openpyxl reads all sheets row by row
- Text/XML → direct UTF-8 decode

**Step 2 — Pre-process**
Cleans whitespace, truncates to 10,000 characters for LLM submission. Generates MD5 hash for change detection.

**Step 3 — LLM extraction**
Calls OpenAI GPT-4o with a structured prompt. Temperature=0 for deterministic output. Returns 5 fields each with `value`, `confidence`, and `source_text`. Falls back to demo mode if no API key is set.

**Step 4 — Validate and score**
Grace period range check, low-confidence field count, overall confidence score, human review flag.

**Step 5 — COB lookup**
If TPL references statutory minimum or is absent, resolves the figure from the COB 2026 table for the pickup country.

**Step 6 — Build API record**
Assembles the final JSON with full provenance, source type, confidence metadata, and API disclaimer.

**Step 7 — Output**
Writes JSON to file; prints formatted terminal summary.

---

## What AI Capability Is Demonstrated

| Capability | How demonstrated |
|---|---|
| **Format-agnostic understanding** | Same LLM prompt works regardless of whether the input came from a PDF, a web page, or an Excel spreadsheet |
| **Unstructured document understanding** | LLM reads natural language T&C text and extracts specific structured fields without templates or rules |
| **Multilingual extraction** | Works on German, Spanish, Italian documents — tested with German source text in web demo |
| **Structured output generation** | LLM outputs strict JSON conforming to a defined schema |
| **Confidence-aware extraction** | Each field carries a confidence score; system routes accordingly |
| **Intelligent data resolution** | TPL "statutory minimum" resolved via COB lookup — absence becomes a correct answer |
| **Human-in-the-loop routing** | Low-confidence records flagged before going live |

---

## Sample Outputs (All Three Source Types)

### PDF source — Hertz Spain
```
Source type: PDF | Supplier: Hertz | Country: ES
TPL:          €70,000,000 personal injury (COB 2026) ✓ HIGH
Grace period: 29 minutes ✓ HIGH
Licence:      EU licence OK; IDP for non-EU; no digital/copies ✓ HIGH
Payment:      Credit card required; debit not accepted ✓ HIGH
Cross-border: Prior authorisation required; Morocco/Kosovo prohibited ~ MEDIUM
Status: APPROVED_AUTO
```

### Excel source — Goldcar Spain
```
Source type: EXCEL | Supplier: Goldcar | Country: ES
2 sheets read: "Rental Conditions", "Additional Rules"
[Same 5 fields extracted from structured spreadsheet rows]
Status: APPROVED_AUTO
```

### Web/HTML source — Sixt Germany
```
Source type: WEB | Supplier: Sixt | Country: DE
TPL:          €7,500,000 personal injury (COB 2026) ✓ HIGH
Grace period: 60 minutes ~ MEDIUM
Licence:      EU/EEA accepted; non-Latin script needs certified translation ✓ HIGH
Payment:      Credit card required; EC-Karte not accepted ✓ HIGH
Cross-border: EU permitted; outside EU needs approval ~ MEDIUM
Status: APPROVED_AUTO
```

---

## Known Limitations of the POC vs. a Production System

| Area | POC | Production |
|---|---|---|
| **LLM model** | General-purpose GPT-4o with basic prompt | v1: GPT-4o with per-supplier few-shot examples; v2: fine-tuned smaller model trained on 750 annotated examples (150 docs × 5 fields) — buildable in weeks 1–4 in parallel with v1 |
| **Terminology normalisation** | LLM must infer that "RC", "Pflichtversicherung", "seguro obligatorio" all mean TPL | Fine-tuned model (v2) learns these patterns from the annotated corpus; human review corrections feed quarterly retraining automatically |
| **Multi-document handling** | One document per run | Full document set per supplier × country (e.g. Avis: General Conditions + Country-Specific Conditions); fields merged with defined precedence (country-specific overrides general) |
| **PDF extraction** | Text-layer PDFs only | OCR (AWS Textract / Tesseract) for scanned documents |
| **Web crawling** | Manual URL or local file | Scheduled crawl with URL monitoring and robots.txt compliance |
| **Excel ingestion** | SFTP or local file | Supplier-specific sheet/column mapping per supplier format |
| **Change detection** | Hash generated but not compared | Hash compared against stored value; unchanged documents skip re-extraction entirely |
| **LLM fallback** | Demo mode only | Auto-failover to Anthropic Claude on low confidence or API failure |
| **Human review** | Email notification | Web interface with source document viewer, inline editing; every correction logged as fine-tuning training example |
| **Knowledge base** | JSON file | PostgreSQL with full version history |
| **COB monitoring** | Static table | Monthly automated check of cobx.org for new editions |
| **Output language** | English only | English (primary) + German (secondary) |
| **Complaint prediction** | Not implemented | v3 (12–18 months post go-live): requires booking → T&C → complaint closed data loop via OTA partnerships |

---

## How to Reproduce / Run It Yourself

### Prerequisites
```bash
pip install pypdf openai openpyxl beautifulsoup4
```

### Demo mode (no API key — works for all source types)
```bash
# PDF source
python3 termsiq_poc.py --demo --local-file sample_tc.txt \
  --supplier Hertz --country ES --source-type pdf

# Excel source
python3 termsiq_poc.py --demo --local-file sample_tc.xlsx \
  --supplier Goldcar --country ES --source-type excel

# Web/HTML source
python3 termsiq_poc.py --demo --local-file sample_tc.html \
  --supplier Sixt --country DE --source-type web
```

### Live mode (with OpenAI API key)
```bash
export OPENAI_API_KEY="sk-your-key-here"

# Hertz Spain — PDF from Hertz website
python3 termsiq_poc.py --supplier Hertz --country ES \
  --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf"

# Hertz Germany — PDF
python3 termsiq_poc.py --supplier Hertz --country DE \
  --url "https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf"

# Web page source
python3 termsiq_poc.py --supplier Sixt --country DE \
  --url "https://www.sixt.de/mietbedingungen/" --source-type web

# Local Excel file (e.g. received from supplier via SFTP)
python3 termsiq_poc.py --supplier Goldcar --country ES \
  --local-file goldcar_conditions.xlsx --source-type excel
```

### Import n8n workflow
1. Open n8n → **+** → **Import from file** → select `poc_workflow.json`
2. Configure credentials: OpenAI API key, SMTP for review emails
3. Update the **Fetch Supplier Document** node URL to your target supplier
4. Click **Execute Workflow**

---

## Files in This POC Package

| File | Description |
|---|---|
| `poc_workflow.json` | n8n workflow — importable directly into n8n |
| `termsiq_poc.py` | Standalone Python script — all three source types |
| `sample_tc.txt` | Sample T&C text file (PDF demo) |
| `sample_tc.xlsx` | Sample T&C Excel file (2 sheets) |
| `sample_tc.html` | Sample T&C HTML web page |
| `termsiq_output_pdf.json` | Sample output — PDF source, Hertz ES |
| `termsiq_output_excel.json` | Sample output — Excel source, Goldcar ES |
| `termsiq_output_web.json` | Sample output — Web source, Sixt DE |
| `poc_documentation.md` | This file |

---

*TermsIQ POC Documentation — Version 1.1 — June 2026*

---

## Overview

This POC demonstrates the core TermsIQ capability: automatically extracting the 5 critical T&C fields from a car rental supplier document, cross-checking TPL against the COB 2026 statutory minimum table, scoring confidence, and outputting a structured JSON record ready for API serving — all without any manual reading of the document.

**Demo recording:** A screen recording of the POC running end-to-end is included separately. It shows: document ingestion → text extraction → OpenAI GPT-4o field extraction → COB lookup → validation scoring → structured JSON output.

---

## Tools Used and Why

| Tool | Role | Why chosen |
|---|---|---|
| **n8n** | Primary workflow orchestration (exportable JSON) | Open-source, self-hostable, supports all required node types (HTTP, Code, OpenAI, email), exportable as JSON for submission, widely used in no-code/low-code AI workflows |
| **Python 3** | Runnable standalone POC script | Demonstrates the same pipeline logic as the n8n workflow but executes immediately without needing n8n installed; useful for validation and demo |
| **OpenAI GPT-4o** | LLM extraction of T&C fields | Strong structured JSON output, multilingual, temperature=0 gives deterministic results; in production used via Azure OpenAI Germany North for data residency |
| **Anthropic Claude** | Fallback LLM (referenced in workflow, configurable in script) | Used when GPT-4o confidence is LOW or primary is unavailable |
| **pypdf** | PDF text extraction | Lightweight Python library for extracting text from PDF documents; handles multi-page documents |
| **COB 2026 table** | TPL statutory minimum reference | Hard-coded lookup table from the Council of Bureaux April 2026 edition; in production this is a database table updated by monthly monitoring |

---

## What the POC Does — Step by Step

### n8n Workflow (`poc_workflow.json`)

The n8n workflow contains 11 nodes representing the full TermsIQ extraction pipeline:

```
[Schedule Trigger]
       │
       ▼
[Fetch Supplier Document]      ← HTTP GET to supplier PDF URL
       │
       ▼
[Extract Text from PDF]        ← n8n built-in PDF extraction
       │
       ▼
[Pre-process & Hash Document]  ← Truncate, clean, generate MD5 hash
       │
       ▼
[OpenAI GPT-4o Extract]        ← LLM extracts 5 fields as structured JSON
       │
       ▼
[Validate & Score Extraction]  ← Confidence scoring, validation rules
       │
       ▼
[TPL needs COB lookup?]        ← IF branch
   YES │                NO │
       ▼                   │
[COB 2026 Lookup]            │
       │                    │
       └────────────────────┘
                │
                ▼
[Requires human review?]       ← IF branch
   YES │               NO │
       ▼                  ▼
[Email to review queue]   [Build API-ready Record]
                                │
                                ▼
                          [Store in Knowledge Base]
```

### Python Script (`termsiq_poc.py`)

The Python script runs the identical logic as 8 sequential steps:

**Step 1 — Fetch/load document**
Fetches the supplier T&C PDF from a URL (Hertz Spain by default) or loads a local file. Any supplier URL or local PDF/text file can be used.

**Step 2 — Extract text**
Uses `pypdf` to extract raw text from the PDF. Falls back to plain text decoding for non-PDF files. Generates an MD5 hash of the raw bytes for change detection.

**Step 3 — Pre-process**
Cleans whitespace, truncates to 10,000 characters for the LLM call (intelligent section detection in production). The hash is stored for future change detection — if the document hasn't changed since last run, extraction is skipped.

**Step 4 — LLM extraction**
Calls OpenAI GPT-4o with a structured system prompt and a field-specific user prompt. Temperature is set to 0 for deterministic, consistent output. The model returns a JSON object with 5 fields, each containing `value`, `confidence`, and `source_text`.

If no `OPENAI_API_KEY` is set, the script runs in **DEMO MODE** with realistic simulated extraction results — allowing the pipeline to be demonstrated without an API key.

**Step 5 — Validate and score**
Applies validation rules:
- Grace period range check (must be 0–480 minutes)
- Counts fields with LOW confidence
- Determines overall confidence (HIGH / MEDIUM / LOW)
- Sets `requires_human_review = True` if 2+ fields are LOW confidence or validation flags are raised

**Step 6 — COB lookup**
If TPL was not explicitly stated (value is `STATUTORY_MINIMUM` or null), looks up the statutory minimum for the pickup country from the built-in COB 2026 table. Returns the personal injury and property damage amounts, data date, and the mandatory COB disclaimer. For countries with no COB data (e.g. Austria, US, Mexico), returns a `requires_manual_verification` flag.

**Step 7 — Build API-ready record**
Assembles the final JSON record including identity fields, provenance metadata, all 5 extracted fields with confidence and source, and API metadata for downstream OTA consumption.

**Step 8 — Output**
Writes the complete record to `termsiq_output.json` and prints a formatted summary to the terminal.

---

## What AI Capability Is Demonstrated

| Capability | How demonstrated |
|---|---|
| **Unstructured document understanding** | LLM reads a multi-page PDF in natural language and extracts specific structured fields without templates or rules |
| **Multilingual extraction** | Prompt supports any language; the same extraction logic works on German, Spanish, Italian documents (configurable via `--country` flag) |
| **Structured output generation** | LLM outputs strict JSON conforming to a defined schema — not free text |
| **Confidence-aware extraction** | Each field carries a confidence score (HIGH/MEDIUM/LOW); the system behaves differently based on confidence |
| **Intelligent resolution of absent data** | TPL "statutory minimum" is not a gap — it's resolved via COB lookup, turning a data absence into a correct answer |
| **Human-in-the-loop routing** | Low-confidence records are automatically flagged for human review before going live |

---

## Sample Output

Running `python3 termsiq_poc.py --demo --local-file sample_tc.txt` produces:

```json
{
  "record_id": "Hertz-ES-1749823200",
  "supplier": "Hertz",
  "pickup_country": "ES",
  "source_url": "local://sample_tc.txt",
  "document_hash": "8c7c641b484bb7c7ebc02ca6dbf90a7d",
  "extracted_at": "2026-06-13T10:00:00+00:00",
  "extraction_model": "gpt-4o",
  "overall_confidence": "HIGH",
  "requires_human_review": false,
  "status": "APPROVED_AUTO",
  "fields": {
    "tpl_amount": {
      "value": "Personal injury: €70,000,000 | Property damage: €15,000,000",
      "confidence": "HIGH",
      "source": "COB Minimum Amount of Coverage 2026 (data date: Dec-25)",
      "resolution_method": "COB_LOOKUP",
      "disclaimer": "Figures provided for information only. COB assumes no responsibility."
    },
    "grace_period_minutes": {
      "value": 29,
      "confidence": "HIGH",
      "source_text": "Reservations not collected within 29 minutes will be cancelled"
    },
    "licence_rules": {
      "value": "Valid driving licence held for minimum 1 year required. International Driving Permit required for non-EU licences. Minimum age 21.",
      "confidence": "HIGH",
      "source_text": "A valid driving licence issued at least 12 months prior"
    },
    "payment_rules": {
      "value": "Credit card required for security deposit. Debit cards not accepted for deposit. Prepaid cards not accepted.",
      "confidence": "HIGH",
      "source_text": "A valid credit card in the main driver's name is required"
    },
    "cross_border_conditions": {
      "value": "Cross-border travel requires prior written authorisation. Travel to Morocco, Albania, Kosovo prohibited without special permit.",
      "confidence": "MEDIUM",
      "source_text": "Cross-border travel must be authorised in advance"
    }
  },
  "api_metadata": {
    "extraction_method": "AI",
    "model_provider": "OpenAI GPT-4o",
    "data_disclaimer": "T&C data is AI-extracted from supplier documents. Verify critical information with the supplier directly."
  }
}
```

---

## Known Limitations of the POC vs. a Production System

| Area | POC | Production |
|---|---|---|
| **Document fetching** | Single URL or local file | SFTP drop, email ingestion, web crawl scheduler, supplier upload portal |
| **Text extraction** | pypdf (text-layer PDFs only) | OCR for scanned documents (e.g. AWS Textract or Tesseract); table extraction for Excel/XML |
| **Token limit** | Truncated to 10,000 characters | Intelligent section detection identifies T&C clauses; strips irrelevant content (vehicle descriptions, marketing) |
| **Change detection** | MD5 hash generated but not compared | Hash compared against stored value in database — unchanged documents skip re-extraction entirely |
| **LLM fallback** | Demo mode only | Automatic failover to Anthropic Claude if GPT-4o fails or returns all-LOW confidence |
| **Human review** | Email notification (n8n) | Dedicated web interface with source document viewer, inline editing, and approval workflow |
| **Knowledge base** | JSON file output | PostgreSQL with full version history, keyed by supplier × country × field |
| **COB reference** | Hard-coded Python dict | Database table; monthly automated monitoring of cobx.org for new editions |
| **Multi-supplier** | Single supplier per run | Parallel processing across all 10 v1 suppliers and all operational markets |
| **Prompt caching** | Not implemented | System prompt cached across all extraction calls (80%+ API cost reduction at volume) |
| **Data residency** | No enforcement | Azure OpenAI Germany North contractually enforced; all infrastructure Germany-region |
| **Audit trail** | JSON file only | Full timestamped version history in PostgreSQL; linked to source document and reviewer identity |
| **Output languages** | English only | English (primary) and German (secondary) for all API responses |

---

## How to Reproduce / Run It Yourself

### Option A — Run the Python script (recommended for quick demo)

**Prerequisites:**
```bash
pip install pypdf openai
```

**Demo mode (no API key needed):**
```bash
python3 termsiq_poc.py --demo --local-file sample_tc.txt
```

**Live mode with OpenAI API key (real extraction):**
```bash
export OPENAI_API_KEY="sk-your-key-here"

# Default: Hertz Spain (fetches PDF from Hertz website)
python3 termsiq_poc.py

# Hertz Germany
python3 termsiq_poc.py --supplier Hertz --country DE \
  --url "https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf"

# Hertz UK
python3 termsiq_poc.py --supplier Hertz --country GB \
  --url "https://images.hertz.com/pdfs/RT_FULL_GB_EN.pdf"

# Local PDF file
python3 termsiq_poc.py --local-file /path/to/supplier_tc.pdf \
  --supplier Sixt --country ES

# Custom output file
python3 termsiq_poc.py --demo --output my_output.json
```

**Output:** `termsiq_output.json` (or your specified output file)

---

### Option B — Import the n8n workflow

**Prerequisites:**
- n8n installed (self-hosted or n8n Cloud)
- OpenAI API credentials configured in n8n
- SMTP credentials configured in n8n (for human review email)

**Steps:**
1. Open your n8n instance
2. Click **+** → **Import from file**
3. Select `poc_workflow.json`
4. Configure credentials:
   - **OpenAI API**: add your OpenAI API key under Credentials → OpenAI API
   - **SMTP**: configure your email server for the human review notification node
5. Update the **Store in Knowledge Base** node URL to your actual API endpoint (or replace with a different output node — e.g. Google Sheets, Airtable, or a database node)
6. Click **Execute Workflow** to run manually, or activate the schedule trigger for daily runs

**To test with a different supplier:**
- Edit the **Fetch Supplier Document** node URL
- Edit the **Pre-process & Hash Document** node to update `supplier` and `pickupCountry` values

---

### Supplier document URLs for testing

| Supplier | Country | URL |
|---|---|---|
| Hertz | Spain | https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf |
| Hertz | Germany | https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf |
| Hertz | UK | https://images.hertz.com/pdfs/RT_FULL_GB_EN.pdf |
| Hertz | Italy | https://images.hertz.com/pdfs/RT_FULL_IT_EN.pdf |

---

## Files in This POC Package

| File | Description |
|---|---|
| `poc_workflow.json` | n8n workflow — importable directly into n8n |
| `termsiq_poc.py` | Standalone Python script — runs the same pipeline end-to-end |
| `termsiq_output.json` | Sample output from a demo run (Hertz / ES) |
| `poc_documentation.md` | This file |

---

*TermsIQ POC Documentation — Version 1.0 — June 2026*
