# TermsIQ MVP — Terminal Output
**Live test results — June 2026**
Model: GPT-4o-mini | Validation: annotation_base.json | Multi-document architecture enabled

---

## TC-05 — Sixt / DE (Web/HTML, German) — MVP Focus Case

**Key improvement over POC:** Grace period sourced from secondary URL (Sixt DE help center). Primary T&C page covers 4 fields; secondary document fills the gap for grace_period_minutes. First live demonstration of the multi-document architecture.

```
✓ LangSmith tracing enabled — project: TermsIQ-POC | endpoint: https://eu.api.smith.langchain.com

============================================================
  TermsIQ MVP — Sixt / DE
============================================================

[Step 1] Fetching document from: https://www.sixt.de/php/terms/view?language=en_US&liso=DE&rtar=000&view=EPP&tlang=de_DE&style=typo3
  ✓ Downloaded 69,077 bytes | Content-Type: text/html; charset=ISO-8859-1

[Step 2] Extracting text from document
  ✓ Loaded as plain text: 68,697 characters
  ✓ Document hash (MD5): 5225744da5231e765e76780a293bcbde

[Step 3] Pre-processing text for LLM submission
  ✓ Processed text: 6,063 characters

[Step 4] Extracting T&C fields via OpenAI GPT-4o
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3,976
  ✓ LangSmith — logged confidence: HIGH (1.0)

[Step 4b] Fetching secondary URL for missing fields: grace_period_minutes
  URL: https://www.sixt.de/help-center/sections/anfahrt-und-ankunft/
  ✓ Downloaded 143,602 bytes | Content-Type: text/html
  ✓ Secondary document: 7,664 characters
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3,825
  ✓ LangSmith — logged confidence: HIGH (1.0)
  ✓ Merged grace_period_minutes: 60 (confidence: HIGH)

[Step 5] Validating extraction and scoring confidence
  ✓ Overall confidence: HIGH
  ✓ Requires human review: False

[Step 6] TPL stated explicitly in document — COB lookup not required

[Step 7] Building API-ready output record

[Step 7b] Comparing extraction against ground truth annotation
  ✓ Accuracy: 5/5 (100%) — meets ≥95% production target

[Step 8] Writing output to termsiq_output.json
  ✓ Saved: termsiq_output.json

============================================================
  EXTRACTION RESULT
============================================================
  Supplier:          Sixt
  Pickup Country:    DE
  Overall Confidence:HIGH
  Status:            APPROVED_AUTO

  ───────────────────────────────────────────────────────
  EXTRACTED FIELDS:
  ───────────────────────────────────────────────────────

  [✓] TPL_AMOUNT (confidence: HIGH)
      EUR 100,000,000 personal injury (max EUR
      12,000,000 per person); property damage included
      Source: "Haftpflichtversicherung mit einer maximalen Deckungssumme bei Personen- und Sach"

  [✓] GRACE_PERIOD_MINUTES (confidence: HIGH)
      60
      Source: "Eine Kulanzzeit von 60 Minuten ab gebuchter Abholzeit"
      ← sourced from secondary URL: sixt.de/help-center/sections/anfahrt-und-ankunft/

  [✓] LICENCE_RULES (confidence: HIGH)
      EU/EEA licence required. Original licence only —
      photocopies and digital licences not accepted.
      Non-German licences require certified translation.
      Source: "Die gltige Fahrerlaubnis ist durch die Vorlage des originalen Fhrerscheins nachz"

  [✓] PAYMENT_RULES (confidence: HIGH)
      Credit and debit cards accepted: Visa, MasterCard,
      Amex, Diners Club, Discover, JCB, China Union Pay.
      Prepaid cards not accepted.
      Source: "Sixt akzeptiert Kredit- und Debit-Karten sowie Digital Wallets von Visa, MasterC"

  [✓] CROSS_BORDER_CONDITIONS (confidence: HIGH)
      4-zone system. Zone I: Western Europe; Zone IV:
      prohibited for all vehicles.
      Source: "Die Fahrzeugwahl kann die Einreise in bestimmte Lnder beschrnken."

============================================================
  MVP COMPLETE
============================================================
  Human review required: NO ✓
  Validation accuracy:   5/5 (100%) — target ≥95%
```

**Run command:**
```powershell
python mvp/termsiq_mvp.py `
  --supplier Sixt --country DE `
  --url "https://www.sixt.de/php/terms/view?language=en_US&liso=DE&rtar=000&view=EPP&tlang=de_DE&style=typo3" `
  --secondary-url "https://www.sixt.de/help-center/sections/anfahrt-und-ankunft/" `
  --validate
```

---

## What the MVP adds over the POC

| Capability | POC | MVP |
|---|---|---|
| Single document extraction | ✓ | ✓ |
| Multi-document architecture | ✗ | ✓ `--secondary-url` |
| Sixt DE grace period | null (absent from T&C page) | **60 min HIGH** |
| Sixt DE payment rules | "Credit and debit accepted" | **Full card brand list** |
| Sixt DE licence rules | null | **EU/EEA rules, translation requirement** |
| LangSmith tracing | ✓ | ✓ Both primary + secondary calls traced |
| GT loaded from JSON | ✓ | ✓ annotation_base.json auto-discovered |

---

## Full MVP results — all suppliers

| Test | Supplier | Source(s) | Accuracy | Status | Human review |
|---|---|---|---|---|---|
| TC-01 | Hertz ES | PDF primary | 5/5 (100%) | PENDING_REVIEW | YES — grace period and licence correctly absent from main PDF |
| TC-02 | Sixt ES | Web/HTML primary | 5/5 (100%) | APPROVED_AUTO | NO |
| TC-03 | Hertz DE | PDF primary | 5/5 (100%) | PENDING_REVIEW | YES — grace period and licence correctly absent from main PDF |
| TC-04 | Goldcar ES | PDF local primary | 5/5 (100%) | APPROVED_AUTO | NO |
| TC-05 | Sixt DE | Web/HTML primary + help center secondary | 5/5 (100%) | APPROVED_AUTO | NO |

**Overall: 25/25 fields (100%)** across 5 suppliers, 3 source types, 3 languages, 6 documents.

---

## Document sources used

| Supplier | Primary | Secondary |
|---|---|---|
| Hertz ES | images.hertz.com/pdfs/RT_FULL_ES_EN.pdf | — |
| Sixt ES | sixt.es/php/terms | — |
| Hertz DE | images.hertz.com/pdfs/RT_FULL_DE_EN.pdf | — |
| Goldcar ES | Local PDF (session-authenticated S3) | — |
| Sixt DE | sixt.de/php/terms | sixt.de/help-center/sections/anfahrt-und-ankunft/ |

---

*TermsIQ MVP — Terminal Output*
*Run date: June 2026 | Model: GPT-4o-mini | Tracing: LangSmith EU endpoint*
*Validation: annotation_base.json (poc/Annotations/) — single source of truth*
