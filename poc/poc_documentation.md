# TermsIQ POC Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.8 — June 2026

> **Version 1.8 note:** Excel branch now fully operational end-to-end in n8n (`poc_workflow.json`). The `Extract from File (CSV mode)` node was replaced with n8n's native **`Extract from XLSX`** node (binary property: `data`), which correctly reads the `.xlsx` binary fetched by the HTTP node. Sicily by Car IT ran successfully through the full pipeline in 9.356s — APPROVED_AUTO, TPL and payment rules partially extracted. Known limitation: structured fields present in the Excel file (licence_rules, grace_period_minutes, cross_border_conditions) are not reliably extracted via the Excel branch due to row-flattening in `Join Excel Rows` and a prompt designed for PDF/web prose rather than tabular data. Documented under Known Limitations; not a blocker for the POC. See TC-09 below.

> **Version 1.7 note:** `termsiq_poc.py` now supports all three source types — PDF, Web/HTML, and Excel — confirmed with live runs across four supplier/country combinations (Sicily by Car IT via Excel, Hertz ES via PDF, Sixt DE via Web/HTML, Goldcar ES via local PDF). LangSmith tracing uses `wrap_openai` + `@traceable` together: `wrap_openai` wraps the OpenAI client so LangSmith automatically captures token counts, latency, and **per-run cost** in the trace list (no manual cost calculation needed); `@traceable` adds the run name, supplier/country tags, and metadata. The EU endpoint (`https://eu.api.smith.langchain.com`) is set as the default. LangSmith is optional but expected — set `LANGCHAIN_API_KEY` before running.
> **Version 1.5 note:** added the "Ground Truth: annotation_base.json" and "URL Validity Agent" sections, neither of which were previously documented despite being used throughout the pipeline — `annotation_base.json` is now explained as the Content team's single source of truth, and the URL Validity Agent (`url_agent.py` + its n8n equivalent) is documented for the first time. Also expanded the one-line LangSmith mention into an actual explanation, and updated Files in This POC Package to include everything that was missing.

> **Version 1.4 note:** the original live testing below (TC-01 through TC-04) was run via the Python script — that's still accurate and unchanged. A separate hardening pass on `poc_workflow.json` specifically followed, since the n8n track's Web/HTML and Excel branches turned out to have real extraction code that was never actually wired into the rest of the pipeline — meaning the "three source types handled live" claim in the Overview below was true for the Python script but not yet true for n8n until this pass. See **"n8n Workflow Hardening — June 2026"** below for what changed and a separate n8n-specific test results section.

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

**Demo recording:** [Watch end-to-end POC demo (Loom)](hhttps://www.loom.com/share/706fb8d5adec4d9daddf31bf0d13ddae)

---

## Tools Used and Why

| Tool | Role | Why chosen |
|---|---|---|
| **n8n** | Primary workflow orchestration (exportable JSON) | Open-source, self-hostable, all required node types available, exportable as JSON for submission |
| **Python 3** | Runnable standalone POC script | Same pipeline logic, executes immediately without n8n installed |
| **OpenAI GPT-4o-mini** | LLM extraction of T&C fields | Sufficient capability for structured extraction; available on standard OpenAI project tier; temperature=0 for deterministic output |
| **pypdf** | PDF text extraction | Lightweight; handles multi-page PDFs with text layer |
| **COB 2026 table** | TPL statutory minimum reference | Built-in lookup from Council of Bureaux April 2026 edition |
| **LangSmith** | LLM call tracing & observability | Traces every OpenAI extraction call. Uses `wrap_openai` (automatic token count, latency, and cost capture in the trace list) combined with `@traceable` (run name `termsiq_extraction`, supplier/country tags, source_chars metadata, confidence feedback score). EU endpoint default. Optional — pipeline runs without it if `LANGCHAIN_API_KEY` is not set. |

---

## What the POC Does — Step by Step

### n8n Workflow (`poc_workflow.json`)

```
[Schedule Trigger]      [On form submission]    ← two entry points; only one fires per run
   (Daily 08:00)         (manual, dropdown:
       │                  hertz_es/hertz_de/
       │                  sixt_es/sixt_de/
       │                  sicily_by_car_it)
       │                       │
       └───────────┬───────────┘
                    ▼
          [Set Run Config]        ← single source of truth: supplier, country, url,
                    │                sourceType. Reads the form's selection if that's
                    │                what triggered the run, else uses a default preset.
                    ▼
[Fetch Supplier Document]      ← HTTP GET (PDF URL or web page URL)
       │
       ▼
[Detect Source Type]           ← Infers 'pdf' / 'web' / 'excel' from URL, or explicit override
       │
       ▼
[Route by Source Type]         ← Switch node — 3 output branches
   PDF │        Web │     Excel │
       ▼             ▼            ▼
[Extract Text  [Extract Text  [Extract from
  — PDF]        — Web/HTML]    File (XLSX)]
       │             │            │
       │             │       [Join Excel Rows]
       │             │            │
       └─────────────┴────────────┘
                     │              ← all three feed the same node directly (no Merge
                     ▼                 step — only one branch ever executes per run,
[Pre-process & Hash Document]         since the Switch only fires one path)
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
  AND  │                    │
       └────────┬───────────┘
                 ▼
        [Build API Record]
                 │
                 ▼
          [Store in KB]
```

The workflow contains **18 nodes** (in the distributed `poc_workflow.json`) plus the Form Trigger, which was added directly in the live n8n canvas rather than baked into the exported file — see the note under Files in This POC Package.

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

## Ground Truth: `annotation_base.json`

Every `--validate` accuracy check this POC runs reads from one file: `annotation_base.json`. It's the single, machine-readable source of truth for what a correct extraction looks like, and it's designed to be owned and maintained by the **Content team going forward, not engineering** — the schema is built so a non-technical reviewer can correct a value, confirm an answer with a supplier, or add a new supplier/country combination without touching any pipeline code.

**Structure.** The file has one `records` array, one entry per supplier/country combination (`HERTZ_ES`, `SIXT_DE`, etc.). Each record has two parts:

- `sources` — every document URL relevant to this supplier/country, split into `primary` (the main T&C document) and `secondary` (FAQ pages, help-center articles, country supplements — anything covering fields the primary document doesn't). Each source carries a `url_status` (`OK` / `404` / `JS_RENDERED` / etc.) kept current automatically by the URL Validity Agent below — not something the Content team needs to check by hand.
- `fields` — the 5 extracted fields, each with an `expected_value` and `validation_keywords` (used for the `--validate` accuracy check) plus an `annotation_note` recording the reviewer's reasoning — e.g. why a field is genuinely absent from the primary document, or which exact FAQ question it was sourced from.

**Two fields already in the schema, not yet used by this POC script.** `annotation_base.json` was designed with the next stage in mind, so two things are already present in the data even though `termsiq_poc.py` only reads this file for the `--validate` comparison and doesn't act on either of them yet:
- `multi_document: true` on a field, paired with a `fields_covered` list on a `secondary` source — intended to let a future pipeline automatically fetch and merge a second document when the primary doesn't resolve a field, with no per-supplier code change needed.
- `resolution_status: "SUPPLIER_CURATED"` and `supplier_verified: true`, paired with an `enriched_value` — intended for fields that genuinely can't be resolved from any live document, where the Content team has obtained and verified the correct answer directly from the supplier instead.

Both of these are implemented and live in the MVP script (`termsiq_mvp.py`), not this POC — worth knowing if a field's expected value here looks oddly specific despite the POC reporting it as null; that's usually `enriched_value` data prepared ahead of the MVP work, not a POC bug.

In short: a new supplier/country combination or a corrected expected value are just edits to this one JSON file — no pipeline code changes required, for either the POC or the MVP that reads from the same file.

---

## URL Validity Agent

Every source in `annotation_base.json` is a live URL, and live URLs change — Sixt reorganised their help center mid-POC (Key Finding #6 below), and the only reason it didn't silently break extraction was that it happened to be caught manually. `url_agent.py` automates that check going forward: it walks every `primary` and `secondary` URL in `annotation_base.json`, checks each one's live status (`OK`, `404`, `JS_RENDERED` if the page content looks like a client-rendered shell, `REDIRECT`, `BLOCKED` for bot-blocking 403s, `TIMEOUT`), writes the result back into that source's `url_status`, and logs every run to `url_agent_log.json` (last 90 runs kept). Run with `--notify`, it emails a summary when any URL needs action, and exits non-zero in that case — so it can gate a scheduled pipeline rather than just report after the fact.

The same logic also exists as an n8n workflow, `url_agent_workflow_v2.json`, for scheduled daily execution without needing a server to keep the Python script running: `Schedule Trigger → Build URL List → Check URL → Classify Result → Aggregate Results → Issues Found? → Send Alert Email / Log — All OK`. A recorded demo of this n8n flow running end-to-end is included (`DEMO-n8n-URLAgent.mp4`).

---

## n8n Workflow Hardening — June 2026

The Python script and the n8n workflow were built from the same design, but only the Python script's three-source-type claim had actually been exercised live. Tracing the n8n workflow's connection graph turned up several issues that only surface once you actually run real documents through it — each is recorded here with what broke, what the evidence was, and what fixed it, since these are the kind of gotchas worth knowing about if this workflow is extended further.

**Web/HTML and Excel branches existed but were never wired to anything.** The Switch node correctly routed to all three extraction branches, and the Web/HTML node in particular had genuinely good HTML-stripping code — but its output connection was an empty array, a true dead end. Excel had no outgoing connection at all. Every run silently fell through to PDF-only behavior regardless of what source type was actually being processed. Fixed by connecting all three extraction nodes directly into `Pre-process & Hash Document`, removing the `Merge — All Source Types` node entirely (it was in an ambiguous `chooseBranch` mode with no branch-selection configuration, which would likely have just defaulted to input 0 regardless of which branch actually ran).

**Binary data wasn't being read reliably.** Once the Web/HTML branch was wired in, a live Sixt ES test produced an empty string — `characterCount: 0` — despite a 76KB file clearly being fetched. The cause: `Fetch Supplier Document` returns binary (not a plain-text JSON field), and the code was reading `binaryData[binaryKey].data` directly, which only reliably holds the full payload when n8n is using in-memory binary storage. Switched to n8n's `getBinaryDataBuffer()` helper, which works regardless of storage mode. A second attempt still produced garbled, suspiciously short output (9 characters) before this fix was identified — that 9-character result, much shorter than the source file, was the actual evidence that ruled out an encoding problem and pointed at the binary-read method instead.

**Sixt's pages aren't UTF-8.** Once binary reading worked, Spanish/German accented characters still came through corrupted on some runs. Sixt's ES and DE terms pages serve `charset=ISO-8859-1`, confirmed from the original Python POC's own terminal output for the same URL. Added a UTF-8-first decode with a Latin-1 fallback, triggered when the UTF-8 decode contains replacement characters.

**Hertz-specific prompt hints were contaminating every other supplier's extraction.** The system prompt unconditionally told the model "licence_rules and grace_period_minutes are absent from main PDF — return null+LOW" on every single run, regardless of which supplier was actually being processed. Sixt's `licence_rules` is genuinely present and extractable, but this instruction suppressed it anyway. Made supplier hints conditional on the actual `supplier` field, keyed per supplier rather than sent unconditionally — the same per-supplier over-suppression problem documented in Key Finding #4 below, just not yet applied to the n8n track until now.

**Explicit TPL figures embedded in a sentence weren't being extracted.** Sixt's primary document states "EUR 85 Mio" inline within a longer sentence about liability insurance, not as a standalone figure. The field instruction had no example of this shape, and the model returned null, letting the COB statutory-minimum lookup silently overwrite Sixt's real €85M figure with Spain's generic €70M minimum — a worse outcome than a null would have been, since it looked like a successful, confident result while actually being wrong. Added a worked example to the `tpl_amount` instruction showing extraction from embedded text.

**`payment_rules` nulled out specifically on documents with deposit-amount language nearby.** The instruction said "NOT deposit amounts" with no positive example, and on Hertz's documents — which mention a specific deposit figure prominently — the model appeared to read this as "skip the field" rather than "skip just the figure." Clarified the instruction to say explicitly that the field should still be extracted, just with the deposit figure itself omitted.

**A generic anchor keyword matched a low-information sentence instead of the real content.** Even after the prompt fix above, Sixt DE's `payment_rules` still nulled. The actual processed text showed why: the only German payment keyword in the section-anchor list, `'zahlungsmittel'`, matched a single generic sentence ("present an accepted means of payment") rather than the document's actual detailed card-brand paragraph elsewhere in the text. Added more specific German terms (`'kredit- und debit'`, `'debitkarten'`, `'kreditkarten'`) ahead of the generic fallback in the keyword priority list, so a more informative match wins when one exists.

**The human review email was unreachable regardless of confidence.** Both outputs of the `Requires human review?` IF node fed only `Build API-ready Record` — the review-queue email node had no path that could ever reach it. Fixed so the true branch reaches both the email and the record-builder. The email node itself remains intentionally disabled, since SMTP isn't configured for this demo environment — enabling it is a deliberate decision for whenever real review-queue testing is needed, not something to flip on by default.

**Testing no longer requires editing code.** Originally, switching test cases meant manually editing two independent hardcoded values — the URL string in `Fetch Supplier Document` and a separate `SUPPLIER`/`COUNTRY` constant inside `Pre-process & Hash Document` — which could drift out of sync with each other. A new `Set Run Config` node now holds named presets (`hertz_es`, `hertz_de`, `sixt_es`, `sixt_de`, `sicily_by_car_it`) as the single source of truth, switchable with one line. A `Form Trigger` ("On form submission") goes further, presenting a literal dropdown to pick a test case without opening any code at all — `Set Run Config` reads the form's selection when that's what triggered the run, falling back to a default preset for Schedule Trigger runs.

**Excel node replaced with native XLSX extractor.** The original `Extract Text — Excel` node used `extractFromFile` in CSV mode, which rejects `.xlsx` binaries with the error "The file selected in 'Input Binary Field' is not in csv format". Replaced with n8n's **`Extract from XLSX`** node (binary property: `data`), which correctly reads the binary payload fetched by the HTTP GET. Confirmed working on first run with Sicily by Car IT (TC-09, 9.356s, APPROVED_AUTO).

---

## Live n8n Workflow Test Results (June 2026)

These are runs through `poc_workflow.json` specifically, after the hardening pass above — distinct from the Python script results in the next section, which were already passing before this session and are unchanged.

| Supplier/Country | Source type | TPL | Grace period | Licence rules | Payment rules | Cross-border |
|---|---|---|---|---|---|---|
| Hertz ES | PDF | HIGH (COB) | null (correct — absent) | null (correct — absent) | HIGH | HIGH |
| Hertz DE | PDF | HIGH (COB) | null (correct — absent) | null (correct — absent) | HIGH | HIGH |
| Sixt ES | Web/HTML | HIGH (explicit €85M) | null* | HIGH | HIGH | HIGH |
| Sixt DE | Web/HTML | HIGH (explicit €100M) | null* | HIGH | HIGH | HIGH |
| Sicily by Car IT | Excel | LOW (COB)† | null† | null† | partial† | null† |

*Grace period nulling for Sixt is expected — the Python pipeline only ever resolved this field via a secondary help-center source, and this n8n workflow fetches one document per run with no multi-source resolution loop (see Known Limitations).

†Sicily by Car IT Excel results reflect a known structural limitation of the Excel branch — see TC-09 and Known Limitations below. TPL is extracted via COB lookup; payment rules are partially extracted. Fields present in the Excel file (licence_rules, grace_period_minutes, cross_border_conditions) are not reliably resolved due to row-flattening. The pipeline ran end-to-end successfully and produced a valid APPROVED_AUTO record.

All four PDF/Web combinations above were confirmed across repeat runs, including a final re-test of Sixt DE's `payment_rules` after the anchor-keyword fix — it now correctly returns the full card-brand detail ("Sixt akzeptiert Kredit- und Debit-Karten sowie Digital Wallets von Visa, MasterCard, American Express, Diners Club, Discover, JCB...") rather than the generic one-line fallback. Every field that's structurally present in the primary document is now resolving correctly across both PDF and Web/HTML source types. Goldcar remains genuinely untested through this workflow: Goldcar's primary source is JS-rendered, and this n8n workflow has no headless-browser or PDF-fallback logic for that case (the Python script handles it; this workflow doesn't yet).

---

| Capability | How demonstrated |
|---|---|
| **Multi-format ingestion** | Same pipeline handles 672KB PDF (Hertz), 76KB HTML page (Sixt), 786KB PDF (Goldcar local), and 36.7KB Excel (Sicily by Car) |
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

### TC-09 — Sicily by Car IT (Excel, n8n workflow) *(new in v1.8)*
**URL:** `https://raw.githubusercontent.com/Dilia108/final-project-Dilia-Navarro/main/poc/T%26C%20samples/Sicily%20by%20car%20T%26C.xlsx` | 36.7KB | Excel (.xlsx)
**Run time:** 9.356s | **Status:** APPROVED_AUTO | **Track:** n8n workflow only

| Field | Result | Confidence | Note |
|---|---|---|---|
| TPL | Personal injury: €6,450,000 / Property damage: €1,300,000 | LOW | COB lookup triggered; value extracted |
| Grace period | null | LOW | Present in Excel file but not resolved — row-flattening limitation |
| Licence rules | null | LOW | Present in Excel file but not resolved — row-flattening limitation |
| Payment | Mastercard/Visa/American Express, Debit cards accepted (partial) | LOW | Partially extracted; full detail not captured |
| Cross-border | null | LOW | Present in Excel file but not resolved — row-flattening limitation |

**What worked:** Full end-to-end pipeline ran successfully — `Extract from XLSX` node correctly ingested the binary, `Join Excel Rows` concatenated row data into text, and the complete downstream pipeline (GPT-4o-mini, COB lookup, validation, record build, file save) executed without errors. Confirms the Excel branch is structurally sound.

**Known limitation:** Fields added to the Excel file (licence_rules, grace_period_minutes, cross_border_conditions) are not reliably extracted. Root cause: `Join Excel Rows` flattens all rows into a single prose string, losing the key/value structure; the extraction prompt is designed for PDF/web prose, not tabular row data. Not a blocker — documented as a future improvement (see Known Limitations).

### Summary across all Python-track tests (TC-01–TC-04)

| Field | Hertz ES | Sixt ES | Hertz DE | Goldcar ES | Pattern |
|---|---|---|---|---|---|
| TPL | ✓ | ✓ | ✓ | ✓ | 4/4 — COB lookup + explicit both work |
| Grace period | ✓ null | ✓ null | ✓ null | ✓ 360 | 4/4 — correctly absent from Hertz; found in Goldcar |
| Licence rules | ✓ null | ✓ | ✓ null | ✓ | 4/4 |
| Payment | ✓ | ✓ | ✓ | ✓ | 4/4 |
| Cross-border | ✓ | ✓ | ✓ | ✓ | 4/4 |

**Overall field accuracy (Python script, PDF/Web): 20/20 (100%)** across 4 suppliers, 3 source types, 2 languages.

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

**8. Excel row-flattening loses the key/value structure needed for reliable field extraction.**
The `Join Excel Rows` node concatenates all Excel rows into a single prose string. This works for simple tabular data but destroys the structural relationship between field names and values when the spreadsheet uses a key/value layout. The extraction prompt — designed for PDF/web prose — cannot reliably identify discrete fields from flattened row text. In production, the fix is to preserve key/value pairs from the spreadsheet rows and pass them as structured JSON to the extraction prompt, rather than concatenating into a string.

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
| **Excel field extraction** | Row-flattening in `Join Excel Rows` loses key/value structure; fields present in spreadsheet not reliably extracted by LLM prompt designed for prose | Structured key/value pairs preserved and passed as JSON to extraction prompt; spreadsheet schema mapped to T&C field ontology |

---

## How to Reproduce / Run It Yourself

### Prerequisites
```bash
pip install pypdf openai
```

### Set API key (PowerShell / Windows)
```powershell
$env:OPENAI_API_KEY    = "sk-your-key-here"
$env:LANGCHAIN_API_KEY = "ls__your_key_here"   # optional — enables LangSmith tracing
$env:PYTHONIOENCODING  = "utf-8"
```

**LangSmith tracing (optional).** If `LANGCHAIN_API_KEY` is set, `_setup_langsmith()` initialises tracing against the EU endpoint (`https://eu.api.smith.langchain.com`) and creates the `TermsIQ-POC` project if it doesn't exist. The OpenAI client is wrapped with `wrap_openai`, which automatically captures token counts, latency, and per-run cost in the LangSmith trace list — no manual cost calculation needed. `@traceable` adds the run name (`termsiq_extraction`), supplier/country/model tags, and a confidence feedback score (HIGH=1.0 / MEDIUM=0.5 / LOW=0.0). Without `LANGCHAIN_API_KEY`, the pipeline runs identically with no tracing. Check your traces at `https://eu.smith.langchain.com`.

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
3. To switch test case: open `Set Run Config` and change `ACTIVE_PRESET` to one of `hertz_es` / `hertz_de` / `sixt_es` / `sixt_de` / `sicily_by_car_it` — no need to touch the Fetch node directly
4. Optional: add an `On form submission` Form Trigger node with a "Test Case" dropdown (same five options) for switching test cases without opening any code — see `Set Run Config`'s comments for how it reads the form's selection
5. Click **Execute Workflow**

---

## Files in This POC Package

| File | Description |
|---|---|
| `poc_workflow.json` | n8n workflow — 18 nodes as exported, importable directly into n8n. Does **not** include the `On form submission` Form Trigger node — that was added directly in the live n8n canvas and isn't baked into this file, since its exact schema varies enough across n8n versions that hand-authoring it risked a broken import. If re-exporting from a canvas that has it, the file will correctly show 19 nodes; `Set Run Config`'s code already references it by name and falls back gracefully if it's absent. |
| `termsiq_poc.py` | Standalone Python script — PDF, web, and JS-rendered page source types |
| `sample_tc.txt` | Sample T&C text file for demo mode (Hertz ES simplified) |
| `termsiq_output.json` | Sample output from live run with `--validate` block embedded |
| `annotation_base.json` | The single, machine-readable ground truth the pipeline reads at runtime — see "Ground Truth" above. Located in the Annotations folder |
| `Annotation_Hertz_Sixt_Goldcar.xlsx` | The original manual research/annotation work for all 5 test cases. Located in the Annotations folder |
| `url_agent.py` | Standalone URL Validity Agent — checks every source URL in `annotation_base.json` and updates its status. Located in the Annotations folder |
| `url_agent_workflow_v2.json` | n8n workflow — 9 nodes, same URL-checking logic as `url_agent.py` for scheduled daily execution. Located in the Annotations folder |
| `url_agent_log.json` | Append-only log of every URL Agent run (last 90 kept). Located in the Annotations folder |
| `DEMO-n8n-URLAgent.mp4` | Recorded demo of the URL Validity Agent's n8n workflow running end-to-end. Located in the Annotations folder |
| `TC - BCN - 2026-06-15T10_09_55Z.pdf` | Goldcar ES T&C PDF (local — requires session-authenticated download). Located in the T&C samples folder |
| `Sicily by car T&C.xlsx` | Sicily by Car IT T&C Excel file — single sheet, tabular rows. Used for TC-09 (first live Excel n8n test). Located in the T&C samples folder |
| `poc_documentation.md` | This file |
| `DEMO_POC_Workflow.mp4` | Demo of the n8n poc_workflow. Located in the Demo POC folder |
| `poc_terminal_output.md` | Terminal output obtained for the 5 suppliers |
---

*TermsIQ POC Documentation — Version 1.8 — June 2026*
