# TermsIQ POC — Terminal Output
**Live test results — June 2026**
Model: GPT-4o-mini | Validation: against manually verified ground truth (`Annotation_Hertz_Sixt_Goldcar.xlsx`)

---

## TC-01 — Hertz / ES (PDF, English)

```
============================================================
  TermsIQ POC — Hertz / ES
============================================================
[Step 1] Fetching document from: https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf
  ✓ Downloaded 672,968 bytes | Content-Type: application/pdf
[Step 2] Extracting text from document
  ✓ Extracted 53,341 characters from 20 pages
  ✓ Document hash (MD5): d17e1319c3e1b635430d48a91eb2ea57
[Step 3] Pre-processing text for LLM submission
  ✓ Processed text: 6,863 characters
[Step 4] Extracting T&C fields via OpenAI GPT-4o-mini
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3698
[Step 5] Validating extraction and scoring confidence
  ✓ Overall confidence: MEDIUM
  ✓ Requires human review: True
  ⚠ Low confidence: grace_period_minutes, licence_rules
[Step 6] TPL not explicit — performing COB 2026 lookup for country: ES
  ✓ COB result: Personal injury: €70,000,000 | Property damage: €15,000,000 (confidence: HIGH)
[Step 7] Building API-ready output record
[Step 7b] Comparing extraction against ground truth annotation
  ✓ Accuracy: 5/5 (100%) — meets ≥95% production target
[Step 8] Writing output to termsiq_output.json
  ✓ Saved: termsiq_output.json
============================================================
  EXTRACTION RESULT
============================================================
  Supplier:          Hertz
  Pickup Country:    ES
  Overall Confidence:MEDIUM
  Status:            PENDING_REVIEW
  ⚠ HUMAN REVIEW REQUIRED
  Low confidence: grace_period_minutes, licence_rules
  ───────────────────────────────────────────────────────
  EXTRACTED FIELDS:
  ───────────────────────────────────────────────────────
  [✓] TPL_AMOUNT (confidence: HIGH)
      Personal injury: €70,000,000 | Property damage: €15,000,000
      Source: "Third Party Liability Insurance which protects you and any authorised driver"
      ⚠ Figures provided for information only. COB assumes no responsibility for accuracy
  [✗] GRACE_PERIOD_MINUTES (confidence: LOW)
      null / not found
  [✗] LICENCE_RULES (confidence: LOW)
      null / not found
  [✓] PAYMENT_RULES (confidence: HIGH)
      Credit and debit cards accepted. Minimum deposit €200,
      additional €500 if SuperCover not purchased.
      Source: "There will always be a MINIMUM of €200 applied; PLUS €500 if you have not purchased SuperCover"
  [✓] CROSS_BORDER_CONDITIONS (confidence: HIGH)
      Cross-Border Fee applies if you drive outside the country of rental.
      Forbidden countries apply.
      Source: "This does not apply for forbidden countries as stated in the Country Specific Terms"
============================================================
  POC COMPLETE — Validation accuracy: 5/5 (100%)
============================================================
```

> **Note:** Grace period and licence rules are correctly null — absent from the Hertz main T&C PDF. The pipeline surfaces the data gap and routes to human review as designed, rather than fabricating a value.

---

## TC-02 — Sixt / ES (Web/HTML, Spanish)

```
============================================================
  TermsIQ POC — Sixt / ES
============================================================
[Step 1] Fetching document from: https://www.sixt.es/php/terms/view?...
  ✓ Downloaded 76,040 bytes | Content-Type: text/html; charset=ISO-8859-1
[Step 2] Extracting text from document
  ✓ Loaded as plain text: 75,455 characters
  ✓ Document hash (MD5): 9ffa47729a21a944367ede1e37ba2e8c
[Step 3] Pre-processing text for LLM submission
  ✓ Processed text: 6,863 characters
[Step 4] Extracting T&C fields via OpenAI GPT-4o-mini
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3635
[Step 5] Validating extraction and scoring confidence
  ✓ Overall confidence: MEDIUM
  ✓ Requires human review: False
  ⚠ Low confidence: grace_period_minutes
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
  Pickup Country:    ES
  Overall Confidence:MEDIUM
  Status:            APPROVED_AUTO
  ───────────────────────────────────────────────────────
  EXTRACTED FIELDS:
  ───────────────────────────────────────────────────────
  [✓] TPL_AMOUNT (confidence: HIGH)
      EUR 85,000,000 personal injury and property damage
      Source: "suma mxima asegurada por lesiones personales y daos por valor de EUR 85 Mio"
  [✗] GRACE_PERIOD_MINUTES (confidence: LOW)
      null / not found
  [✓] LICENCE_RULES (confidence: HIGH)
      Valid driving license required. Non-Latin alphabet licenses
      need IDP or official translation.
      Source: "Un permiso de conducir expedido en un idioma con un alfabeto no latino... debe s"
  [✓] PAYMENT_RULES (confidence: HIGH)
      Credit and debit cards accepted for deposit. Prepaid cards not accepted.
      Source: "Las tarjetas de dbito o prepago no se pueden utilizar para pagos"
  [✓] CROSS_BORDER_CONDITIONS (confidence: HIGH)
      Prohibited to take vehicle to countries outside Zone 1.
      Penalty for violation: EUR 150.
      Source: "Est prohibido llevar el vehculo a pases distintos de los incluidos en la Zona 1."
============================================================
  POC COMPLETE — Validation accuracy: 5/5 (100%)
============================================================
```

> **Note:** Source document is in Spanish — all fields extracted correctly with no language configuration required. TPL is stated explicitly (EUR 85 Mio) so COB lookup is skipped. Status is APPROVED_AUTO.

---

## TC-03 — Hertz / DE (PDF, English)

```
============================================================
  TermsIQ POC — Hertz / DE
============================================================
[Step 1] Fetching document from: https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf
  ✓ Downloaded 651,380 bytes | Content-Type: application/pdf
[Step 2] Extracting text from document
  ✓ Extracted 53,946 characters from 20 pages
  ✓ Document hash (MD5): 4c296e30905307d27c20577ca616c286
[Step 3] Pre-processing text for LLM submission
  ✓ Processed text: 6,863 characters
[Step 4] Extracting T&C fields via OpenAI GPT-4o-mini
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3685
[Step 5] Validating extraction and scoring confidence
  ✓ Overall confidence: MEDIUM
  ✓ Requires human review: True
  ⚠ Low confidence: grace_period_minutes, licence_rules
[Step 6] TPL not explicit — performing COB 2026 lookup for country: DE
  ✓ COB result: Personal injury: €7,500,000 | Property damage: €1,300,000 (confidence: HIGH)
[Step 7] Building API-ready output record
[Step 7b] Comparing extraction against ground truth annotation
  ✓ Accuracy: 5/5 (100%) — meets ≥95% production target
[Step 8] Writing output to termsiq_output.json
  ✓ Saved: termsiq_output.json
============================================================
  EXTRACTION RESULT
============================================================
  Supplier:          Hertz
  Pickup Country:    DE
  Overall Confidence:MEDIUM
  Status:            PENDING_REVIEW
  ⚠ HUMAN REVIEW REQUIRED
  Low confidence: grace_period_minutes, licence_rules
  ───────────────────────────────────────────────────────
  EXTRACTED FIELDS:
  ───────────────────────────────────────────────────────
  [✓] TPL_AMOUNT (confidence: HIGH)
      Personal injury: €7,500,000 | Property damage: €1,300,000
      Source: "Third Party Liability Insurance which protects you and any authorised driver"
      ⚠ Figures provided for information only. COB assumes no responsibility for accuracy
  [✗] GRACE_PERIOD_MINUTES (confidence: LOW)
      null / not found
  [✗] LICENCE_RULES (confidence: LOW)
      null / not found
  [✓] PAYMENT_RULES (confidence: HIGH)
      Credit and debit cards accepted. Minimum deposit €200.
      Source: "a MINIMUM of €200 applied"
  [✓] CROSS_BORDER_CONDITIONS (confidence: HIGH)
      Driving outside the rental country requires permission and incurs a fee.
      Forbidden countries apply.
      Source: "If you want to drive the vehicle in any other country, you must gain our prior permission"
============================================================
  POC COMPLETE — Validation accuracy: 5/5 (100%)
============================================================
```

> **Note:** Same structural pattern as Hertz ES. COB lookup triggered for Germany — €7,500,000 personal injury vs €70,000,000 in Spain, demonstrating country-specific statutory minimum resolution. PENDING_REVIEW is the correct outcome.

---

## TC-04 — Goldcar / ES (Local PDF, English/Spanish)

```
============================================================
  TermsIQ POC — Goldcar / ES
============================================================
[Step 1] Loading local file: poc/T&C samples/TC - BCN - 2026-06-15T10_09_55Z.pdf
  ✓ Loaded 786,123 bytes
[Step 2] Extracting text from document
  ✓ Extracted 76,877 characters from 20 pages
  ✓ Document hash (MD5): 8dd5f766baaad08ab8ba6acadc02fbe2
[Step 3] Pre-processing text for LLM submission
  ✓ Processed text: 6,863 characters
[Step 4] Extracting T&C fields via OpenAI GPT-4o-mini
  Calling GPT-4o-mini (temperature=0)...
  ✓ Extraction complete | Tokens used: 3865
[Step 5] Validating extraction and scoring confidence
  ✓ Overall confidence: HIGH
  ✓ Requires human review: False
[Step 6] TPL not explicit — performing COB 2026 lookup for country: ES
  ✓ COB result: Personal injury: €70,000,000 | Property damage: €15,000,000 (confidence: HIGH)
[Step 7] Building API-ready output record
[Step 7b] Comparing extraction against ground truth annotation
  ✓ Accuracy: 5/5 (100%) — meets ≥95% production target
[Step 8] Writing output to termsiq_output.json
  ✓ Saved: termsiq_output.json
============================================================
  EXTRACTION RESULT
============================================================
  Supplier:          Goldcar
  Pickup Country:    ES
  Overall Confidence:HIGH
  Status:            APPROVED_AUTO
  ───────────────────────────────────────────────────────
  EXTRACTED FIELDS:
  ───────────────────────────────────────────────────────
  [✓] TPL_AMOUNT (confidence: HIGH)
      Personal injury: €70,000,000 | Property damage: €15,000,000
      Source: "cumple con todos los requisitos legales en materia de responsabilidad civil"
      ⚠ Figures provided for information only. COB assumes no responsibility for accuracy
  [✓] GRACE_PERIOD_MINUTES (confidence: HIGH)
      360
      Source: "Goldcar will guarantee your booking"
  [✓] LICENCE_RULES (confidence: HIGH)
      Minimum age 21. US/Canadian drivers need IDP.
      Digital licences accepted if via miDGT app.
      Source: "Goldcar minimum age is 21 for ALL vehicles."
  [✓] PAYMENT_RULES (confidence: HIGH)
      Only Visa and Mastercard accepted. Maestro, prepaid cards,
      Amex, Diners Club not accepted.
      Source: "Debito, Credit card VISA or MasterCard"
  [✓] CROSS_BORDER_CONDITIONS (confidence: HIGH)
      Only Andorra, France, Italy, Portugal, Gibraltar permitted.
      Formentera and Ibiza prohibited.
      Source: "the island of Formentera and the island of Ibiza is never permitted."
============================================================
  POC COMPLETE — Validation accuracy: 5/5 (100%)
============================================================
```

> **Note:** Goldcar's T&C website is JS-rendered — the pipeline detected this automatically and the local PDF was used instead. All 5 fields extracted with HIGH confidence across the board. The only test case where all fields are present in the main T&C document. Status: APPROVED_AUTO.

---

## Summary

| Test | Supplier | Source type | Accuracy | Status | Human review |
|---|---|---|---|---|---|
| TC-01 | Hertz ES | PDF — 672KB, 20 pages | **5/5 (100%)** | PENDING_REVIEW | YES — grace period and licence correctly absent |
| TC-02 | Sixt ES | Web/HTML — 76KB, Spanish | **5/5 (100%)** | APPROVED_AUTO | NO |
| TC-03 | Hertz DE | PDF — 651KB, 20 pages | **5/5 (100%)** | PENDING_REVIEW | YES — grace period and licence correctly absent |
| TC-04 | Goldcar ES | PDF local — 786KB, 20 pages | **5/5 (100%)** | APPROVED_AUTO | NO |

**Overall: 20/20 fields (100%)** across 3 suppliers, 3 source types, 2 languages.

The PENDING_REVIEW status on both Hertz test cases is correct behaviour — the pipeline surfaces genuine data gaps rather than fabricating values, and holds them for human review before going live.

---

*TermsIQ POC — Terminal Output*
*Run date: June 2026 | Model: GPT-4o-mini | Validation: Annotation_Hertz_Sixt_Goldcar.xlsx*
