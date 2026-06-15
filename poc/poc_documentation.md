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
[Fetch Supplier Document]      ← HTTP GET (PDF URL, web page URL, or Excel SFTP)
       │
       ▼
[Detect Source Type]           ← Infers 'pdf' / 'web' / 'excel' from URL extension
       │                         or explicit sourceType field in supplier config
       ▼
[Route by Source Type]         ← Switch node — 3 output branches
   PDF │        Web │     Excel │
       ▼             ▼            ▼
[Extract Text  [Extract Text  [Extract Text
  — PDF]        — Web/HTML]    — Excel]
  n8n built-in  Strip tags,    Parse sheets,
  PDF extractor  HTML entities  row-by-row text
       │             │            │
       └─────────────┴────────────┘
                     │
                     ▼
[Merge — All Source Types]     ← All branches produce { text, sourceType, supplier, ... }
                     │
                     ▼
[Pre-process & Hash Document]  ← Truncate, clean, MD5 hash (identical for all sources)
                     │
                     ▼
[OpenAI GPT-4o Extract]        ← 5 T&C fields as structured JSON (few-shot prompt)
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

The workflow contains **17 nodes**. Source-type detection and the three parallel extraction branches (PDF, Web/HTML, Excel) are the key addition over a single-source pipeline. All three branches converge at the Merge node and produce identical JSON, so every downstream node is source-agnostic.

### Python Script (`termsiq_poc.py`) — 8 Steps

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
| **LLM model** | General-purpose GPT-4o with basic prompt | v1: GPT-4o with per-supplier few-shot examples drawn from the annotated ground truth set; prompts tuned per field type based on observed error patterns |
| **Terminology normalisation** | LLM must infer that "RC", "Pflichtversicherung", "seguro obligatorio" all mean TPL | Per-supplier few-shot examples in the prompt teach the model the terminology patterns specific to each supplier and language; human review corrections feed back into prompt refinement |
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
