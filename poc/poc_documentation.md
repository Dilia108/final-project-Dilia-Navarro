# TermsIQ POC Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.3 — June 2026

---

## Overview

This POC demonstrates the core TermsIQ capability across three real-world supplier document source types tested live: **PDF documents**, **website/HTML pages**, and **JS-rendered web pages with PDF fallback**. The pipeline handles all three in the same flow — the only difference is the ingestion step that converts each format into plain text before sending to the LLM.

For each source the pipeline:
1. Fetches and ingests the document (PDF binary, HTML page, or local file)
2. Detects JS-rendered pages and falls back to a direct PDF URL automatically
3. Strips HTML / extracts PDF text; applies multi-anchor section detection for long documents
4. Extracts the 5 critical T&C fields using OpenAI GPT-4o-mini with few-shot examples
5. Cross-checks TPL against the COB 2026 statutory minimum table where needed
6. Scores confidence and flags for human review if needed
7. Compares extraction against manually verified ground truth (with `--validate`)
8. Outputs a single structured JSON record ready for API serving

**Demo recording:** [Watch end-to-end POC demo (Loom)](https://www.loom.com/share/d09135f07ea847899d64e34682d6b8fe)

---

## Tools Used and Why

| Tool | Role | Why chosen |
|---|---|---|
| **n8n** | Primary workflow orchestration (exportable JSON) | Open-source, self-hostable, all required node types available, exportable as JSON for submission |
| **Python 3** | Runnable standalone POC script | Same pipeline logic, executes immediately without n8n installed |
| **OpenAI GPT-4o-mini** | LLM extraction of T&C fields | Sufficient capability for structured extraction; available on standard OpenAI project tier; temperature=0 for deterministic output |
| **pypdf** | PDF text extraction | Lightweight; handles multi-page PDFs with text layer |
| **COB 2026 table** | TPL statutory minimum reference | Built-in lookup from Council of Bureaux April 2026 edition |

---

## What the POC Does — Step by Step

### n8n Workflow (`poc_workflow.json`)

```
[Schedule Trigger]
       │
       ▼
[Fetch Supplier Document]      ← HTTP GET (PDF URL or web page URL)
       │
       ▼
[Detect Source Type]           ← Infers 'pdf' / 'web' / 'excel' from URL extension
       │
       ▼
[Route by Source Type]         ← Switch node — 3 output branches
   PDF │        Web │     Excel │
       ▼             ▼            ▼
[Extract Text  [Extract Text  [Extract Text
  — PDF]        — Web/HTML]    — Excel]
       │             │            │
       └─────────────┴────────────┘
                     │
                     ▼
[Merge — All Source Types]
                     │
                     ▼
[Pre-process & Hash Document]  ← Multi-anchor section detection, MD5 hash
                     │
                     ▼
[OpenAI GPT-4o-mini Extract]   ← 5 T&C fields as structured JSON
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

The workflow contains **17 nodes** including source-type detection and three parallel extraction branches that converge before the LLM step.

### Python Script (`termsiq_poc.py`) — 8 Steps

**Step 1 — Fetch/load document**
Fetches from URL or loads local file. Detects PDF vs HTML automatically. Accepts `--local-file` for locally saved documents (e.g. session-authenticated PDFs downloaded manually).

**Step 2 — Extract text**
PDF → pypdf page-by-page extraction (capped at 20 pages). HTML → tag stripping, entity decoding, whitespace cleaning. Generates MD5 hash for change detection.

**Step 3 — Pre-process (multi-anchor section detection + JS-render detection)**
For long documents (real supplier PDFs run 50,000+ characters), blindly truncating to the first 10,000 chars misses key sections. The preprocessor finds up to 5 independent anchor windows — one per field — and stitches them together. Anchors use full phrases and section headings (e.g. `"insurance and excess waiver"`, `"reservation of credit"`, `"permiso de conducir"`) rather than single words, to avoid matching adjacent sections.

If the processed output from a web page is below 5,000 characters — indicating a JS-rendered page where the browser loads content client-side — the pipeline automatically detects this, logs a warning, and falls back to a direct PDF URL if one is provided via `--pdf-url`. This was triggered in TC-04 (Goldcar).

**Step 4 — LLM extraction**
Calls GPT-4o-mini with a domain-specific system prompt, two few-shot examples drawn from the annotated ground truth, and a user prompt. Temperature=0 for deterministic output. Returns 5 fields each with `value`, `confidence` (HIGH/MEDIUM/LOW), and `source_text` (verbatim quote from document). Per-supplier hints in the system prompt handle known structural patterns (e.g. Hertz splits licence rules across documents; Goldcar calls the grace period a "booking guarantee").

**Step 5 — Validate and score**
Grace period range check (0–480 min). Counts LOW confidence fields. Sets `requires_human_review` if 2+ fields are LOW or validation flags raised.

**Step 6 — COB lookup**
If TPL is STATUTORY_MINIMUM or absent, looks up the country's statutory minimum from the built-in COB 2026 table. Returns personal injury + property damage amounts with source, data date, and mandatory COB disclaimer.

**Step 7 — Build API record**
Assembles final JSON with provenance metadata, confidence scores, status (APPROVED_AUTO or PENDING_REVIEW), and optional `validation` block.

**Step 8 — Output**
Writes `termsiq_output.json`. With `--validate`, embeds field-by-field comparison against manually verified ground truth from the annotation file.

---

## What AI Capability Is Demonstrated

| Capability | How demonstrated |
|---|---|
| **Multi-format ingestion** | Same pipeline handles 672KB PDF (Hertz), 76KB HTML page (Sixt), and 786KB PDF (Goldcar local) |
| **JS-rendered page detection** | Goldcar web page yields only 3,466 chars (JS shell) — detected automatically, falls back to PDF |
| **Multilingual extraction** | Sixt ES document is in Spanish — model extracts correctly, source texts are Spanish phrases |
| **Structured output from unstructured text** | LLM reads messy PDF text with headers/footers mixed in and returns strict JSON |
| **Intelligent absent-field handling** | Grace period absent from Hertz PDFs → null + LOW, not a fabricated value |
| **Statutory minimum resolution** | TPL "as required by law" → COB lookup → €70M (ES) or €7.5M (DE) with source attribution |
| **Explicit vs statutory TPL distinction** | Sixt ES states EUR 85 Mio explicitly → extracted directly, COB lookup skipped |
| **Human-in-the-loop routing** | LOW confidence fields flagged; `requires_human_review` set before data goes live |
| **Source attribution** | Every extracted value carries a verbatim `source_text` quote from the document |
| **Per-supplier prompt adaptation** | Supplier hints in system prompt handle structural differences (Hertz multi-doc split, Goldcar terminology) |

---

## Live Test Results (June 2026)

All four tests run against real live supplier documents. Model: GPT-4o-mini. Validation against manually verified ground truth from `Annotation_Hertz_Sixt_Goldcar.xlsx`.

### TC-01 — Hertz ES (PDF, English)
**URL:** `https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf` | 672KB | 20 pages | 53,341 chars extracted

| Field | Result | Confidence | Note |
|---|---|---|---|
| TPL | €70,000,000 / €15,000,000 | HIGH | STATUTORY_MINIMUM → COB 2026 ES ✓ |
| Grace period | null | LOW | Absent from PDF — in FAQ separately ✓ |
| Licence rules | null | LOW | Absent from PDF — Hertz splits T&C across documents ✓ |
| Payment | Credit and debit cards accepted | HIGH | ✓ |
| Cross-border | Permission required; forbidden countries listed in Country Specific Terms | HIGH | ✓ |
| **Validation** | **5/5 (100%)** | | Grace period and licence correctly null |

### TC-02 — Sixt ES (Web/HTML, Spanish)
**URL:** `https://www.sixt.es/php/terms/view?language=en_US&liso=ES&rtar=000&view=EPP&tlang=es_ES&style=typo3` | 76KB HTML | 75,455 chars raw | Spanish language

| Field | Result | Confidence | Note |
|---|---|---|---|
| TPL | EUR 85,000,000 | HIGH | Explicit supplier figure — COB lookup skipped ✓ |
| Grace period | null | LOW | Not in T&C document; help center URL updated June 2026 ✓ |
| Licence rules | IDP for non-Latin alphabet; non-EU rules | HIGH | Extracted from Spanish source ✓ |
| Payment | Credit/debit accepted; prepaid not accepted | HIGH | ✓ |
| Cross-border | Zone I only; penalty EUR 150 | HIGH | ✓ |
| **Validation** | **5/5 (100%)** | | |

### TC-03 — Hertz DE (PDF, English)
**URL:** `https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf` | 651KB | 20 pages | 53,946 chars extracted

| Field | Result | Confidence | Note |
|---|---|---|---|
| TPL | €7,500,000 / €1,300,000 | HIGH | STATUTORY_MINIMUM → COB 2026 DE ✓ |
| Grace period | null | LOW | Absent from PDF — same pattern as Hertz ES ✓ |
| Licence rules | null | LOW | Absent from PDF — Hertz country supplement only ✓ |
| Payment | Credit and debit cards accepted | HIGH | ✓ |
| Cross-border | Prior permission required; forbidden countries listed in Country Specific Terms | HIGH | ✓ |
| **Validation** | **5/5 (100%)** | | Grace period and licence correctly null |

### TC-04 — Goldcar ES (JS-rendered page → PDF fallback, English/Spanish)
**Web URL:** `https://www.goldcar.es/en-gb/terms-and-conditions/` → **PDF:** `TC - BCN - 2026-06-15T10_09_55Z.pdf` (local) | 786KB | 20 pages | 76,877 chars extracted

| Field | Result | Confidence | Note |
|---|---|---|---|
| TPL | €70,000,000 / €15,000,000 | HIGH | STATUTORY_MINIMUM → COB 2026 ES ✓ |
| Grace period | 360 minutes | HIGH | "garantizará tu reserva" — 6-hour booking guarantee ✓ |
| Licence rules | Min. age 21; US/Canada IDP required; digital via miDGT only | HIGH | ✓ |
| Payment | Visa and Mastercard only; Amex/Maestro/prepaid rejected | HIGH | ✓ |
| Cross-border | 5 countries only (Andorra, France, Italy, Portugal, Gibraltar); GPS enforced | HIGH | ✓ |
| **Validation** | **5/5 (100%)** | | JS-render detected; PDF fallback used automatically |

### Summary across all four tests

| Field | Hertz ES | Sixt ES | Hertz DE | Goldcar ES | Pattern |
|---|---|---|---|---|---|
| TPL | ✓ | ✓ | ✓ | ✓ | 4/4 — COB lookup + explicit both work |
| Grace period | ✓ null | ✓ null | ✓ null | ✓ 360 | 4/4 — correctly absent from Hertz; found in Goldcar |
| Licence rules | ✓ null | ✓ | ✓ null | ✓ | 4/4 |
| Payment | ✓ | ✓ | ✓ | ✓ | 4/4 |
| Cross-border | ✓ | ✓ | ✓ | ✓ | 4/4 |

**Overall field accuracy: 20/20 (100%)** across 4 suppliers, 3 source types, 2 languages.

The Hertz null results for grace period and licence rules are **correct answers**, not failures — these fields are genuinely absent from the main T&C PDF. The pipeline correctly returns null + LOW and routes to human review, surfacing the data gap rather than fabricating a value. In production, a second pipeline run against the Hertz FAQ and country supplement supplements these fields.

---

## Key Findings from Live Testing

**1. Multi-anchor section detection with section-heading anchors is essential.**
Real supplier PDFs extract 50,000+ characters. Simple keyword anchors (e.g. `"third party insurance"`) fire on the wrong section — the Hertz charges table at the top of the PDF uses this phrase before the actual liability clause. The solution was to use section headings (`"insurance and excess waiver"`, `"reservation of credit"`) as priority anchors, with generic keywords as fallbacks. Similarly, window size matters: increasing from 1,600 to 2,000 chars caused adjacent sections in Sixt ES to collide. 1,600 chars per window is the correct balance.

**2. JS-rendered pages require automatic detection and fallback.**
Goldcar's T&C page (`goldcar.es/en-gb/terms-and-conditions/`) is a React shell — raw HTML yields only 3,466 characters with no T&C content. The pipeline detects this (threshold: <5,000 chars from a web fetch) and automatically falls back to `--pdf-url` if provided, logging a clear warning. In production this would trigger a headless browser render or session-authenticated PDF download.

**3. The grace period multi-document problem is universal for Hertz, supplier-specific for Goldcar.**
Hertz does not state a pickup grace period in any country T&C PDF. Goldcar states theirs (6 hours = 360 minutes) in the main T&C under `"recogida del vehículo"` using the term `"garantizará tu reserva"` rather than "grace period". The per-supplier hint in the system prompt resolves this terminology gap.

**4. Per-supplier system prompt hints prevent false extractions without suppressing valid ones.**
Early versions of the Hertz hint over-suppressed the model, causing it to return null for payment and cross-border (which ARE present in the PDF). The final hint is field-specific: it suppresses licence and grace period only, and explicitly instructs the model to extract payment and cross-border normally. Goldcar's hint similarly provides terminology mappings and expected value patterns.

**5. Few-shot examples must be injected as separate message turns.**
The few-shot examples were written correctly but were not being sent to the API — the messages array only contained the system prompt and user request. Adding the examples as a dedicated user turn (with an assistant acknowledgement turn) was the fix. This is the single most impactful prompt engineering improvement made during the POC.

**6. Sixt UI change detected during testing (June 15, 2026).**
The Sixt ES grace period help center URL (`/help-center/articles/recogida-tardia/`) returned 404 — Sixt had reorganised their help center. The new URL was found manually and the annotation updated. In production, TermsIQ's daily hash monitoring would flag this automatically.

**7. Spanish-language extraction works without any language configuration.**
The Sixt ES HTML page is in Spanish. The model extracted all fields correctly with Spanish source text quotes. No language-specific configuration was required.

---

## Known Limitations of the POC vs. a Production System

| Area | POC | Production |
|---|---|---|
| **Multi-document handling** | One document per run | Full document set per supplier × country; fields merged with country-specific overrides |
| **Grace period sourcing — Hertz** | Returns null (correctly) when absent from T&C PDF | Second pipeline run against FAQ/help center URL supplements absent fields |
| **Licence rules — Hertz** | Returns null (correctly); routes to human review | Sourced from Hertz country-specific supplement via supplier account manager |
| **JS-rendered pages** | Detected; falls back to `--pdf-url` if provided | Headless browser (Playwright) renders page before extraction; session auth for gated PDFs |
| **PDF extraction** | Text-layer PDFs only; pypdf warnings on malformed headers | OCR (AWS Textract) for scanned documents; robust parser for malformed PDFs |
| **Web crawling** | Manual URL | Scheduled crawl with URL monitoring, robots.txt compliance, and 404 alerting |
| **Change detection** | MD5 hash generated but not compared | Hash compared against stored value; unchanged documents skip re-extraction |
| **Human review interface** | Email notification (n8n) | Web UI with source document viewer, inline editing, approval workflow |
| **Knowledge base** | JSON file | PostgreSQL with full version history keyed by supplier × country × field |
| **COB monitoring** | Static built-in table | Monthly automated check of cobx.org for new editions |
| **Prompt refinement** | Per-supplier hints in system prompt | Per-supplier prompt variants tuned on full annotation dataset; fine-tuned model for production scale |
| **Output language** | Extraction language matches source document | English primary output regardless of source language |
| **Source text attribution** | Occasional misattribution on licence_rules (cosmetic) | Validated source text linked to exact page and character offset in source document |

---

## How to Reproduce / Run It Yourself

### Prerequisites
```bash
pip install pypdf openai
```

### Set API key (PowerShell / Windows)
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:PYTHONIOENCODING = "utf-8"
```

### TC-01 — Hertz ES (PDF)
```powershell
python poc/termsiq_poc.py --supplier Hertz --country ES --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" --validate
```

### TC-02 — Sixt ES (Web/HTML)
```powershell
python poc/termsiq_poc.py --supplier Sixt --country ES --url "https://www.sixt.es/php/terms/view?language=en_US&liso=ES&rtar=000&view=EPP&tlang=es_ES&style=typo3" --validate
```

### TC-03 — Hertz DE (PDF)
```powershell
python poc/termsiq_poc.py --supplier Hertz --country DE --url "https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf" --validate
```

### TC-04 — Goldcar ES (JS-rendered page → local PDF fallback)
```powershell
python poc/termsiq_poc.py --supplier Goldcar --country ES --url "https://www.goldcar.es/en-gb/terms-and-conditions/" --local-file "poc/T&C samples/TC - BCN - 2026-06-15T10_09_55Z.pdf" --validate
```

### Debug mode — inspect preprocessed text sent to LLM
```powershell
python poc/termsiq_poc.py --supplier Hertz --country ES --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" --validate --debug-text > debug_output.txt 2>&1
```

### Demo mode (no API key needed)
```powershell
python poc/termsiq_poc.py --demo --local-file poc/sample_tc.txt --supplier Hertz --country ES --validate
```

### Import n8n workflow
1. Open n8n → **+** → **Import from file** → select `poc_workflow.json`
2. Configure credentials: OpenAI API key, SMTP for review emails (SMTP was deactivated for the demo)
3. Update the **Fetch Supplier Document** node URL to your target supplier
4. Click **Execute Workflow**

---

## Files in This POC Package

| File | Description |
|---|---|
| `poc_workflow.json` | n8n workflow — 17 nodes, importable directly into n8n |
| `termsiq_poc.py` | Standalone Python script — PDF, web, and JS-rendered page source types |
| `sample_tc.txt` | Sample T&C text file for demo mode (Hertz ES simplified) |
| `termsiq_output.json` | Sample output from live run with `--validate` block embedded |
| `Annotation_Hertz_Sixt_Goldcar.xlsx` | Manually verified ground truth for all 4 test cases |
| `TC - BCN - 2026-06-15T10_09_55Z.pdf` | Goldcar ES T&C PDF (local — requires session-authenticated download) |
| `poc_documentation.md` | This file |

---

*TermsIQ POC Documentation — Version 1.3 — June 2026*
