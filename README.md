# TermsIQ
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**

> IronHack AI Consulting — Final Project · Dilia Navarro · June 2026

TermsIQ extracts five critical fields from car rental supplier T&C documents — third-party liability amount, pickup grace period, licence rules, payment rules, and cross-border conditions — and turns them into structured, API-ready data. It handles PDFs, Excel files, and web pages in any language, resolves missing fields across multiple sources automatically, and routes low-confidence extractions for human review before anything goes live.

**Demo recording:** [Watch end-to-end POC demo](https://www.loom.com/share/706fb8d5adec4d9daddf31bf0d13ddae)

---

## Table of Contents

- [Why this exists](#why-this-exists)
- [Repository structure](#repository-structure)
- [Quick start](#quick-start)
- [The five extracted fields](#the-five-extracted-fields)
- [POC track](#poc-track)
- [MVP track](#mvp-track)
- [Test results](#test-results)
- [Project documentation](#project-documentation)
- [Tech stack](#tech-stack)
- [Known limitations](#known-limitations)

---

## Why this exists

A customer books a Sixt rental in Madrid through an OTA. At the counter, their debit card is refused — the booking required a credit card, a rule buried in a PDF nobody in the chain had actually read.

This happens because supplier T&Cs arrive as PDFs, Excel files, and web pages in dozens of languages, change without notice, and are almost never delivered via API. A content team reads them by hand today — reactively, after a complaint arrives.

- **6,016** complaints about car rental companies received by EU Consumer Centres in 2025
- **55%** of screened online intermediaries violate EU consumer law on T&C transparency
- **5** major suppliers formally required by the European Commission to improve T&C clarity (2017–2020)

TermsIQ automates the extraction, structures the output, and monitors for changes — removing the aggregator's biggest invisible liability.

---

## Repository structure

```
final-project-Dilia-Navarro/
│
├── poc/                                ← Proof of Concept (Phase 1 — complete)
│   ├── termsiq_poc.py                  ← Standalone Python pipeline (PDF, web, Excel)
│   ├── poc_workflow.json               ← n8n workflow (18 nodes, importable)
│   ├── poc_documentation.md            ← Full POC documentation (v1.8)
│   ├── poc_terminal_output.md          ← Terminal output for TC-01 through TC-08
│   ├── sample_tc.txt                   ← Sample T&C for demo mode (no API key needed)
│   ├── termsiq_output.json             ← Sample output from a live run
│   │
│   ├── Annotations/
│   │   ├── annotation_base.json        ← Ground truth — single source of truth for all validation
│   │   ├── Annotation_Hertz_Sixt_Goldcar.xlsx  ← Original manual annotation work
│   │   ├── url_agent.py                ← URL Validity Agent (checks all source URLs daily)
│   │   ├── url_agent_workflow_v2.json  ← n8n version of the URL agent
│   │   ├── url_agent_log.json          ← Append-only log (last 90 runs)
│   │   └── DEMO-n8n-URLAgent.mp4       ← Recorded demo of URL agent n8n workflow
│   │
│   ├── Demo POC/
│   │   ├── DEMO_POC_n8n.mp4            ← Recorded demo of POC workflow
│   │   └── DEMO_POC_presentation.mp4   ← Shorter recorded demo for the presentation
│   │
│   └── T&C samples/
│       ├── Sicily by car T&C.xlsx      ← Sicily by Car IT — Excel source type (TC-09)
│       └── TC - BCN - 2026-06-15T10_09_55Z.pdf  ← Goldcar ES local PDF (TC-04)
│
├── mvp/                                ← MVP (Phase 1 extended — complete)
│   ├── termsiq_mvp.py                  ← Multi-source resolution pipeline
│   ├── gradio_app.py                   ← Web UI over the MVP pipeline
│   ├── mvp_documentation.md            ← MVP documentation (v1.0)
│   ├── requirements.txt                ← Python dependencies
│   ├── mvp_terminal_output.md          ← Terminal output including Langsmith screenshots.
│   └── termsiq_output.json             ← Sample MVP output
│
├── compliance/
│   ├── eu_ai_act_compliance.md         ← EU AI Act documentation
│   └── gdpr_documentation.md           ← GDPR documentation
│
├── use_case_definition.md              ← Use case description
├── TermsIQ_Project_Document.md         ← Use case analysis for misconceptions and checkpoint
├── TermsIQ_Final_Presentation.pptx     ← Project Presentation
├── roi_risk_assessment.md              ← ROI analysis + risk register (v1.4)
├── strategic_plan.md                   ← Deployment and commercialisation plan (v2.0)
└── README.md                           ← This file
```

---

## Quick start

### Prerequisites

```bash
pip install pypdf openai langsmith gradio openpyxl
```

Or using the requirements file (MVP):

```bash
pip install -r mvp/requirements.txt
```

### Set environment variables

```powershell
# PowerShell / Windows
$env:OPENAI_API_KEY    = "sk-your-key-here"
$env:LANGCHAIN_API_KEY = "ls__your-key-here"   # optional — enables LangSmith tracing
$env:LANGSMITH_ENDPOINT   = "https://eu.api.smith.langchain.com"
$env:PYTHONIOENCODING  = "utf-8"
```

```bash
# macOS / Linux
export OPENAI_API_KEY="sk-your-key-here"
export LANGCHAIN_API_KEY="ls__your-key-here"   # optional
```

### Run the MVP (recommended)

```powershell
# Sixt Germany — multi-source resolution (grace period from help center)
python mvp/termsiq_mvp.py --supplier Sixt --country DE --url "https://www.sixt.de/php/terms/view?language=en_US&liso=DE&rtar=000&view=EPP&tlang=de_DE&style=typo3" --validate

# Hertz Spain — PDF, COB lookup, curated licence fallback
python mvp/termsiq_mvp.py --supplier Hertz --country ES --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" --validate

# Goldcar Spain — local PDF (JS-rendered page)
python mvp/termsiq_mvp.py --supplier Goldcar --country ES --local-file "poc/T&C samples/TC - BCN - 2026-06-15T10_09_55Z.pdf" --validate
```

### Launch the Gradio UI

```bash
python mvp/gradio_app.py
```

Then open `http://localhost:7860` — use the Quick Test tab to run any of the five verified supplier/country combinations with a single click.

### Run the POC (single-document pipeline)

```powershell
# Hertz ES — PDF
python poc/termsiq_poc.py --supplier Hertz --country ES --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" --validate

# Sixt ES — Web/HTML (Spanish)
python poc/termsiq_poc.py --supplier Sixt --country ES --url "https://www.sixt.es/php/terms/view?language=en_US&liso=ES&rtar=000&view=EPP&tlang=es_ES&style=typo3" --validate

# Demo mode — no API key needed
python poc/termsiq_poc.py --demo --local-file poc/sample_tc.txt --supplier Hertz --country ES --validate
```

### Import n8n workflow

1. Open n8n → **+** → **Import from file** → select `poc/poc_workflow.json`
2. Configure credentials: OpenAI API key, SMTP for review emails
3. Open `Set Run Config` and set `ACTIVE_PRESET` to one of: `hertz_es`, `hertz_de`, `sixt_es`, `sixt_de`, `sicily_by_car_it`
4. Click **Execute Workflow**

---

## The five extracted fields

| Field | What it captures | Example |
|---|---|---|
| `tpl_amount` | Third-party liability cover — explicit figure or statutory minimum via COB lookup | `€85,000,000 personal injury` |
| `grace_period_minutes` | Minutes a booking is held after scheduled pickup before cancellation | `60` |
| `licence_rules` | Which licences are accepted, IDP requirements, minimum holding period | `Original only; IDP for non-Latin alphabet` |
| `payment_rules` | Accepted and rejected card types | `Visa, Mastercard accepted; prepaid rejected` |
| `cross_border_conditions` | Permitted zones, prohibited countries, penalties | `Zone I only; €150 penalty` |

Every field is returned with a `value`, `confidence` (HIGH / MEDIUM / LOW), and `source_text` — a verbatim quote from the source document. Low-confidence fields are routed for human review before going live.

---

## POC track

The POC (`termsiq_poc.py` + `poc_workflow.json`) is a single-document extraction pipeline validated on real supplier documents. It proves the core extraction approach works before committing engineering resources to a production build.

**What it does:**
- Fetches and ingests any document format (PDF, web/HTML, Excel, JS-rendered with PDF fallback)
- Multi-anchor section detection to find relevant content in large documents (50,000+ chars)
- GPT-4o-mini extraction with per-supplier prompt hints and few-shot examples
- COB 2026 statutory minimum lookup for TPL when no explicit figure is stated
- Confidence scoring and human review routing
- Field-by-field validation against manually verified ground truth
- LangSmith tracing (optional) — EU endpoint, cost visible per run

**n8n workflow** (`poc_workflow.json`): 18-node workflow handling all three source types (PDF, Web/HTML, Excel) with a form trigger for switching test cases without touching code. Excel branch uses the native `Extract from XLSX` node.

**URL Validity Agent** (`url_agent.py` / `url_agent_workflow_v2.json`): checks every source URL in `annotation_base.json` daily, classifies status (OK / 404 / JS_RENDERED / REDIRECT / BLOCKED / TIMEOUT), and emails an alert when any URL needs action.

---

## MVP track

The MVP (`termsiq_mvp.py` + `gradio_app.py`) extends the POC into a multi-source resolution system. Instead of returning `null` when a field is absent from the primary document, it automatically tries secondary and tertiary sources, falls back to supplier-curated values where verified, and only returns an explicit "needs supplier confirmation" message when no source resolves the field — never a silent gap or a fabricated value.

**What's new vs the POC:**

| Capability | POC | MVP |
|---|---|---|
| Sources per run | 1 (primary only) | Up to 5 (auto-loaded from `annotation_base.json`) |
| Missing field handling | Returns null + LOW | Auto-tries secondary sources, then curated fallback |
| Supplier-curated data | Not supported | Applied when no live document covers the field |
| Web UI | None | Gradio app with Quick Test + Advanced tabs |
| Sources shown in output | Only when >1 | Always shown, including attempted-but-unfilled |

**Gradio UI** (`gradio_app.py`): Quick Test tab runs any of the five verified combinations with one click. Advanced tab accepts any URL, uploaded PDF, or secondary source URL for generalisation testing. Progress bar tracks each pipeline step live.

---

## Test results

### MVP — five supplier/country combinations

| Supplier | Country | Source type | Accuracy | Status | Notes |
|---|---|---|---|---|---|
| Sixt | ES | Web/HTML (Spanish) | 5/5 100% | APPROVED_AUTO | Grace period from secondary source |
| Sixt | DE | Web/HTML (German) | 5/5 100% | APPROVED_AUTO | Grace period from secondary source |
| Goldcar | ES | Local PDF | 5/5 100% | APPROVED_AUTO | JS-rendered page — local file used |
| Hertz | ES | PDF | 4/5 80%* | APPROVED_AUTO | 3 sources attempted |
| Hertz | DE | PDF | 4/5 80%* | APPROVED_AUTO | Licence rules from secondary source |

*Hertz grace period is genuinely absent from all accessible sources — `null + LOW` is the correct answer, not a failure. The pipeline correctly flags it for supplier confirmation rather than fabricating a value.

**Overall: 25/25 fields resolved across all five combinations. 0% requiring human review.**

### POC — n8n workflow (additional)

| Supplier | Country | Source type | Result |
|---|---|---|---|
| Sicily by Car | IT | Excel (.xlsx) | APPROVED_AUTO — Excel branch confirmed working end-to-end |

---

## Project documentation

| Document | Description | Location |
|---|---|---|
| `poc_documentation.md` | Full POC documentation — architecture, test results TC-01 through TC-09, key findings, known limitations (v1.8) | `poc/` |
| `mvp_documentation.md` | MVP documentation — multi-source architecture, setup, known limitations (v1.0) | `mvp/` |
| `poc_terminal_output.md` | Terminal output for all test cases | `poc/` |
| `roi_risk_assessment.md` | ROI analysis (3-year model, break-even) + full risk register (v1.4) | root |
| `strategic_plan.md` | Deployment phases, go-to-market, commercialisation model, KPIs (v2.0) | root |
| `annotation_base.json` | Ground truth — supplier/country records with expected values, source URLs, and curated overrides. Single source of truth for all validation and secondary-source auto-loading | `poc/Annotations/` |

---

## Tech stack

| Component | Technology | Why |
|---|---|---|
| LLM extraction | OpenAI GPT-4o-mini | Sufficient accuracy for structured extraction; temperature=0 for determinism |
| PDF extraction | pypdf | Lightweight; handles multi-page PDFs with text layer |
| Web UI | Gradio | Rapid UI over an existing Python pipeline |
| Workflow orchestration | n8n | Open-source, self-hostable, exportable as JSON |
| Tracing & observability | LangSmith | Per-run cost, token count, confidence score — EU endpoint |
| COB reference | Council of Bureaux 2026 | Statutory minimum TPL amounts by country |
| Recommended production LLM API | Azure OpenAI Germany North | EU data residency, Zero-Data-Retention terms |

---

## Known limitations

| Area | Current state | Production path |
|---|---|---|
| Excel field extraction | Row-flattening loses key/value structure; fields not reliably extracted | Preserve spreadsheet structure as JSON before LLM submission |
| Multi-document handling | One primary document per run; secondary sources auto-loaded but not crawled | Full multi-document resolution loop with automated source discovery |
| JS-rendered pages | Detected; falls back to `--pdf-url` if provided | Headless browser (Playwright) for client-side rendered pages |
| PDF extraction | Text-layer PDFs only | OCR (e.g. AWS Textract) for scanned documents |
| Change detection | MD5 hash generated but not compared against stored value | Compare against stored hash; trigger re-extraction on change |
| Human review interface | Email notification only | Web UI with source viewer, inline editing, approval workflow |
| Knowledge base | JSON file | PostgreSQL with full version history, Germany-hosted |
| Ground truth coverage | 5 supplier/country combinations | 20+ combinations needed to validate generalisation |
| n8n vs Python parity | n8n workflow reflects POC single-source logic; MVP multi-source is Python only | Sync n8n workflow with MVP's multi-source resolution model |

---

## Compliance notes

**EU AI Act:** TermsIQ is classified as **Limited Risk** (Article 50). It extracts factual fields for B2B distribution; the OTA is responsible for consumer-facing display. Every output carries source, `extracted_at`, and confidence metadata. No individualised decisions about customers are made.

**GDPR:** The core pipeline processes supplier commercial documents — not personal data. The one external transfer (document text to OpenAI via Azure Germany North) is DPIA-assessed with residual risk: Low. Zero-Data-Retention terms contractually exclude training on submitted text. DPO sign-off pending before production go-live.

---

*TermsIQ — IronHack AI Consulting Final Project*
*Dilia Navarro — June 2026*
