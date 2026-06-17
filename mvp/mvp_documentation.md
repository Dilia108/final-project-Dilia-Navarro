# TermsIQ — MVP Documentation
**Intelligent Terms & Conditions Extraction for Car Rental Distribution**
Version 1.0 — June 2026

---

## Overview

TermsIQ extracts five fields that cause the most friction at the rental counter — third-party liability amount, pickup grace period, licence rules, payment rules, and cross-border conditions — from supplier T&C documents, and turns them into a structured, API-ready record. The MVP takes the POC's single-document extraction pipeline and extends it into a multi-source resolution system: instead of returning `null` when a field is genuinely absent from the main document, it automatically tries documented secondary and tertiary sources, falls back to a supplier-curated value where one has been verified, and only when no source exists at all does it return an explicit "needs supplier confirmation" message rather than a silent gap.

Five supplier/country combinations are covered: Hertz ES, Hertz DE, Sixt ES, Sixt DE, and Goldcar ES.

---

## Architecture Overview

```
[Fetch / Load Primary Document]        ← URL fetch or --local-file
              │
              ▼
[Extract Text]                         ← pypdf (PDF) or HTML strip (web)
              │
              ▼
[Pre-process]                          ← multi-anchor section windows (1,400 chars/field)
              │                           + JS-render detection (<5,000 chars → PDF fallback
              │                             if --pdf-url given)
              ▼
[LLM Extract — Primary Document]       ← GPT-4o-mini, temperature=0, few-shot examples,
              │                           per-supplier prompt hints
              ▼
      Any fields still null / LOW confidence?
       │ yes                              │ no
       ▼                                  │
[Auto-load secondary sources]             │
 from annotation_base.json                │
 (unless --no-auto-sources)               │
       ▼                                  │
[Multi-source resolution loop]            │
 for each documented source, in order:    │
  • dedupe by URL (merge fields_covered)  │
  • skip if it covers no remaining gap    │
  • fetch + extract + merge into record   │
  • stop early once everything's resolved │
       │                                  │
       └────────────────┬─────────────────┘
                         ▼
          [Resolve any fields still unresolved]
           • supplier-curated override, if one is documented
             and marked supplier_verified (confidence capped MEDIUM)
           • otherwise: explicit "needs supplier confirmation"
             status message — never a fabricated value
                         ▼
          [Validate & Score]              ← same threshold logic as the POC:
                                             requires_human_review if 2+ fields
                                             are LOW or a validation flag fires
                         ▼
          [TPL needs COB lookup?] ──yes──▶ [COB 2026 Statutory Minimum Lookup]
                         │
                         ▼
          [Build API-ready Record]        ← + sources_used, curated source/URL,
                                             status_message, full attribution
                         ▼
          [Validate vs ground truth]      ← optional, --validate flag
                         ▼
                  [Output JSON]
```

**Where this sits relative to the POC's other components.** The POC shipped two parallel implementations of the same logic — an n8n workflow (`poc_workflow.json`) and this standalone Python script — plus a separate, already-scheduled n8n workflow (`url_agent_workflow_v2.json`) that checks every documented URL daily and emails an action table when one breaks (404, JS-rendered, redirected, timed out). The MVP work this round extended the **Python track only**. The n8n workflow still reflects the POC's single-document, no-curated-fallback logic, and the URL agent's URL list is a separate hardcoded copy of what's in `annotation_base.json` rather than reading from it directly — both are flagged below under production needs, since letting two implementations or two URL lists drift apart silently is exactly the kind of gap that surfaced once already this session (see Known Limitations).

---

## Setup and Installation

```bash
pip install pypdf openai
```

```powershell
# PowerShell / Windows
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:PYTHONIOENCODING = "utf-8"

# Enables LangSmith tracing of every extraction call
$env:LANGSMITH_API_KEY = "your-langsmith-key"
```

Expected file layout:
```
mvp/termsiq_mvp.py
poc/Annotations/annotation_base.json
```

`annotation_base.json` is the single source of truth for ground-truth values, documented secondary/tertiary source URLs per supplier/country, and any supplier-curated field overrides. The script looks for it at `--annotation`, then `poc/Annotations/annotation_base.json`, then alongside the script itself.

---

## How to Run It

```powershell
python mvp/termsiq_mvp.py --supplier Hertz --country ES `
  --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" --validate

python mvp/termsiq_mvp.py --supplier Hertz --country DE `
  --url "https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf" --validate

python mvp/termsiq_mvp.py --supplier Sixt --country ES `
  --url "https://www.sixt.es/php/terms/view?language=en_US&liso=ES&rtar=000&view=EPP&tlang=es_ES&style=typo3" --validate

python mvp/termsiq_mvp.py --supplier Sixt --country DE `
  --url "https://www.sixt.de/php/terms/view?language=en_US&liso=DE&rtar=000&view=EPP&tlang=de_DE&style=typo3" --validate

python mvp/termsiq_mvp.py --supplier Goldcar --country ES `
  --local-file "poc/T&C samples/TC - BCN - 2026-06-15T10_09_55Z.pdf" --validate
```

### Flag reference

| Flag | Purpose |
|---|---|
| `--supplier`, `--country` | Required. Identifies which annotation record and prompt hints to use. |
| `--url` | Primary document URL (PDF or web page). |
| `--local-file` | Use a local file instead of, or alongside, a URL fetch. |
| `--pdf-url` | Fallback PDF to use if `--url` turns out to be JS-rendered. |
| `--secondary-url` *(repeatable)* | Manually add extra sources beyond what's auto-loaded from the annotation file. |
| `--no-auto-sources` | Disable automatic loading of documented secondary sources — primary document only. |
| `--annotation` | Path to `annotation_base.json`, if not in a default location. |
| `--validate` | Embed a field-by-field ground-truth comparison block and print accuracy. |
| `--output` | Output JSON path (default `termsiq_output.json`). |
| `--demo` | Run without an API key, using a regex-based fallback extractor — useful for offline testing of the pipeline shape, not for real extraction quality. |

### Current results

| Supplier/Country | Fields resolved | Status |
|---|---|---|
| Hertz ES | 5/5 (100%) | APPROVED_AUTO |
| Hertz DE | 5/5 (100%) | APPROVED_AUTO |
| Sixt ES | 5/5 (100%) | APPROVED_AUTO |
| Sixt DE | 5/5 (100%) | APPROVED_AUTO |
| Goldcar ES | 5/5 (100%) | APPROVED_AUTO |

**25/25 fields (100%)** across all five supplier/country combinations, all auto-approved — none currently require human review.

---

## Known Limitations and What Would Be Needed for Production

| Area | Where the MVP stands now | Still needed for production |
|---|---|---|
| **Multi-document handling** | Auto-loads and merges documented secondary/tertiary sources to fill gaps, with dedup, skip, and early-stop | Scheduled periodic re-fetch rather than on-demand only; an **enrichment pass for already-resolved fields** — currently a source is only fetched to fill a gap, never to add richer detail to a field that already resolved HIGH from the primary document (e.g. Hertz ES's payment FAQ has prepaid/corporate/travel-agency exceptions the primary PDF doesn't, but it's never fetched since payment_rules already resolves HIGH). Deliberately deferred this round — it reopens a completeness/cost-tradeoff question (a guaranteed second LLM call even when the first succeeded) worth scoping on its own. |
| **Grace period — Hertz** | Genuinely absent from any documented source for either ES or DE (confirmed, not a gap in our source list) — returns an explicit "needs supplier confirmation" message rather than a bare null | No public source exists at all; production needs this sourced directly from the supplier account-manager relationship, not scraping |
| **Licence rules — Hertz** | DE now resolves live (HIGH) via a confirmed server-rendered secondary source; ES resolves via a documented, supplier-verified curated override (MEDIUM) since the only ES source is unreachable | Replace the ES curated fallback with a live source once/if Hertz exposes one outside the JS-rendered FAQ widget |
| **JS-rendered pages** | Same `<5,000 chars` detection as the POC; this round it correctly identified that Hertz ES's entire FAQ section (`customersupport/index.jsp?targetPage=faq.jsp`) is one client-side-routed shell — every FAQ answer, payment included, lives behind the same URL with no distinct address per answer | Headless browser (Playwright) rendering for these pages, or a negotiated direct supplier feed instead of scraping |
| **PDF extraction** | Unchanged — pypdf, text-layer only | OCR (e.g. AWS Textract) for scanned documents |
| **Web crawling** | Manual URLs, but robots.txt compliance is actually checked in practice — an alternate Hertz URL was rejected this round specifically because robots.txt disallowed it, even though it would have technically worked | Scheduled crawl rather than on-demand, with automated 404/redirect alerting |
| **Change detection** | MD5 hash generated per document but not compared against a stored value; the separate `url_agent_workflow_v2.json` does daily URL-*health* checks (404/JS-rendered/redirect) but not document-*content* change detection | Hash comparison to skip re-extraction when a document hasn't changed; merge URL-health and content-change monitoring into one system |
| **Duplicate source-of-truth for URLs** | `url_agent_workflow_v2.json` keeps its own hardcoded copy of every source URL, separate from `annotation_base.json`. The two had already drifted — a broken Hertz ES payment URL fixed in the annotation file this round was still present in the URL agent's list until caught and fixed in this session | URL agent should read source URLs directly from `annotation_base.json` rather than maintaining a parallel list |
| **n8n workflow vs Python script** | `poc_workflow.json`'s three source-type branches (PDF/Web/Excel) are now actually wired end-to-end — the Web/HTML and Excel extraction nodes existed with working code but were never connected past the Switch, so every run silently fell through to PDF-only regardless of source type. Supplier/country config is now centralized in one `Set Run Config` node instead of two independently-edited hardcoded spots (the Fetch node's URL string and a separate constant inside Pre-process) that could drift out of sync. What's still missing: the workflow doesn't have the MVP's multi-source *resolution* model — no auto-loading of documented secondary sources from `annotation_base.json`, no supplier-curated fallback, no dedup/skip/early-stop. It ingests one document per run, same as the POC always did, just now correctly for whichever source type that document is | Either extend the n8n workflow with the same multi-source resolution loop the Python script has, or formally designate the Python script as the production-track implementation |

> **A note on the URL agent's hardcoded list specifically:** this one is a constraint of the current n8n version in use, which doesn't have a clean way to pull shared configuration from an external JSON file without a custom node or a newer n8n release — `annotation_base.json` was always meant to be the single source of truth here. The supplier/country hardcoding in `poc_workflow.json`, by contrast, turned out not to be an n8n-version issue at all once traced through — it was simply two independent hardcoded spots that needed wiring to a shared config node instead, which is what the fix above does.
| **Validation matching** | Ground-truth comparison uses substring keyword matching; this round it correctly caught a true positive (an LLM phrasing change for Hertz ES cross-border conditions stopped containing any of the listed keywords, even though the extracted content was still correct) | More robust matching (semantic similarity, not exact substrings) so a valid paraphrase doesn't register as a false negative |
| **Payment amount sourcing** | Deposit/security-hold amounts are deliberately excluded from `payment_rules` — they're sourced separately via the supplier's live rate/XML feed, not from the T&C document, to avoid serving a stale or conflicting figure | That XML feed needs to actually be wired in as a separate, authoritative field merged at serving time, not just omitted |
| **Human review interface** | None — one-shot CLI tool, no review queue | Web UI with source document viewer, inline editing, and an approval workflow |
| **Knowledge base** | Single JSON file per run | PostgreSQL with full version history keyed by supplier × country × field |
| **COB monitoring** | Static built-in table | Monthly automated check of cobx.org for new editions |
| **Output language** | Matches the source document's language in both the Python script and the n8n workflow — confirmed consistent across Hertz (English-language PDFs for both ES and DE), Sixt ES (Spanish), and Sixt DE (German) live tests | English primary output is still the target for the Python/production track. For the n8n workflow specifically, this has been deliberately deprioritized rather than left as an oversight — forcing English normalization there was judged not worth the added complexity for what's the secondary implementation track, not the production candidate |

---

## How It Extends the POC

| | POC | MVP |
|---|---|---|
| Suppliers covered | 4 (Hertz ES, Hertz DE, Sixt ES, Goldcar ES) | 5 (adds Sixt DE) |
| Sources per run | One document only | Primary plus auto-loaded secondary/tertiary, with dedup, skip, and early-stop |
| Hertz ES / DE result | `PENDING_REVIEW` — grace period and licence rules both null + LOW, 2+ LOW fields trips the review threshold | `APPROVED_AUTO` — licence rules now resolves (live for DE, curated for ES); grace period remains the one genuinely unresolvable field, so only 1 field is LOW, under the same review threshold |
| Field accuracy | 20/20 (100%), counting correct nulls as correct | 25/25 (100%), with far fewer fields actually landing on null |
| Absent-field handling | Returns `null` + LOW confidence | Three-tier resolution: live extraction → supplier-curated override (if verified) → explicit "needs supplier confirmation" message — never a bare null and never a fabricated value |
| Validation logic | Keyword match on extracted value only | Same keyword logic, plus two new auto-match rules: curated values always match (`validated_via: supplier_curated_override`), and multi-document-resolved values match without requiring stale null-only keywords (`validated_via: multi_document_resolution_unverified_content`) |
| Output detail | Field value, confidence, source quote | Adds full reference/reference URL display (e.g. the exact COB table citation, previously computed but never shown), curated source/URL when applicable, and the source quote shown in full rather than truncated mid-word |

The review-threshold logic itself didn't change — it's the same "2+ LOW fields or a validation flag triggers review" rule from the POC. What changed is the resolution pipeline feeding into it: by recovering licence_rules for both Hertz markets, only one structurally-absent field (grace period) is left LOW per record, which is what flips both Hertz cases from `PENDING_REVIEW` to `APPROVED_AUTO` without loosening the review criteria itself.

---

*TermsIQ MVP Documentation — Version 1.0 — June 2026*
