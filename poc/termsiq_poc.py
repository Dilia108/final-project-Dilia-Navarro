#!/usr/bin/env python3
"""
TermsIQ POC — T&C Extraction Pipeline
======================================
Demonstrates the core TermsIQ capability:
  1. Fetch a real supplier T&C document (Hertz Spain PDF)
  2. Extract the 5 critical fields using OpenAI GPT-4o
  3. Cross-check TPL against the COB 2026 statutory minimum table
  4. Score confidence and flag for human review if needed
  5. Output a structured JSON record ready for API serving

Usage:
  export OPENAI_API_KEY="your-key-here"
  python3 termsiq_poc.py

  # To use a different supplier/country:
  python3 termsiq_poc.py --supplier Sixt --country DE --url "https://car-rental.sixt.com/php/terms"

  # To test with a local PDF:
  python3 termsiq_poc.py --local-file /path/to/supplier_tc.pdf --supplier Hertz --country ES
"""

import os
import sys
import json
import hashlib
import argparse
import textwrap
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# COB 2026 Statutory Minimum Reference Table
# Source: Council of Bureaux, April 2026 edition
# Disclaimer: Figures for information only. COB assumes no responsibility.
# ---------------------------------------------------------------------------
COB_2026 = {
    "DE": {"personal_injury": "€7,500,000",  "property_damage": "€1,300,000",  "data_date": "Dec-25", "confidence": "HIGH"},
    "ES": {"personal_injury": "€70,000,000", "property_damage": "€15,000,000", "data_date": "Dec-25", "confidence": "HIGH"},
    "IT": {"personal_injury": "€6,450,000",  "property_damage": "€1,300,000",  "data_date": "Dec-25", "confidence": "HIGH"},
    "GB": {"personal_injury": "£1,200,000",  "property_damage": "£1,200,000",  "data_date": "Dec-25", "confidence": "HIGH"},
    "NO": {"personal_injury": "Unlimited",   "property_damage": "€8,484,643",  "data_date": "Dec-25", "confidence": "HIGH"},
    "CH": {"personal_injury": "CHF 5,000,000 per claim", "property_damage": None, "data_date": "Nov-24", "confidence": "HIGH"},
    "AT": {"personal_injury": None, "property_damage": None, "data_date": "Oct-21", "confidence": "NONE",
           "note": "No data submitted to COB — manual verification required"},
    "FR": {"personal_injury": "Unlimited", "property_damage": "Unlimited", "data_date": "Mar-22", "confidence": "MEDIUM",
           "note": "Unlimited — not displayable as a numeric value"},
    "NL": {"personal_injury": "€6,070,000", "property_damage": "€1,220,000", "data_date": "Nov-20", "confidence": "MEDIUM",
           "note": "Stale — COB data from Nov-20"},
    "BE": {"personal_injury": "€129,550,507", "property_damage": "Unlimited", "data_date": "Dec-25", "confidence": "HIGH"},
    "PL": {"personal_injury": "€5,210,000", "property_damage": "€1,050,000", "data_date": "Dec-25", "confidence": "HIGH"},
    "PT": {"personal_injury": "€6,450,000", "property_damage": "€1,300,000", "data_date": "Dec-25", "confidence": "HIGH"},
    "US": {"personal_injury": None, "property_damage": None, "data_date": None, "confidence": "NONE",
           "note": "Outside COB scope — US statutory minimums vary by state"},
    "MX": {"personal_injury": None, "property_damage": None, "data_date": None, "confidence": "NONE",
           "note": "Outside COB scope — verify with Mexican insurance regulator"},
}

EXTRACTION_PROMPT_SYSTEM = """You are a specialist in car rental terms and conditions extraction.
Your task is to extract exactly five specific fields from a car rental supplier T&C document.
You must respond ONLY with valid JSON — no preamble, no explanation, no markdown code fences.
If a field is not mentioned or cannot be determined from the document, use null for the value
and set confidence to LOW. Be precise and conservative — only extract what is explicitly stated."""

EXTRACTION_PROMPT_USER = """Extract the following 5 fields from this car rental T&C document.
Supplier: {supplier} | Pickup Country: {country}

Fields to extract:
1. tpl_amount: The third party liability coverage amount. If the document states
   'statutory minimum applies' or similar, set value to 'STATUTORY_MINIMUM'.
2. grace_period_minutes: Grace period before no-show cancellation, as an integer (minutes).
3. licence_rules: Key licence acceptance rules — what licences are accepted, rejected,
   or require translation. Be specific about country/type combinations.
4. payment_rules: Which payment methods are accepted for deposit and rental.
   Distinguish credit card vs debit card.
5. cross_border_conditions: Any restrictions or requirements for taking the vehicle
   across national borders.

For each field provide:
- value: the extracted information (string, integer, or null)
- confidence: HIGH (clearly stated), MEDIUM (implied/inferred), LOW (absent/very unclear)
- source_text: the exact phrase supporting the extraction (max 100 chars), or null

Document text (first 10,000 characters):
{text}

Respond with ONLY this JSON structure:
{{
  "tpl_amount": {{"value": null, "confidence": "LOW", "source_text": null}},
  "grace_period_minutes": {{"value": null, "confidence": "LOW", "source_text": null}},
  "licence_rules": {{"value": null, "confidence": "LOW", "source_text": null}},
  "payment_rules": {{"value": null, "confidence": "LOW", "source_text": null}},
  "cross_border_conditions": {{"value": null, "confidence": "LOW", "source_text": null}}
}}"""


def banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def step(n, msg):
    print(f"\n[Step {n}] {msg}")


def fetch_document(url: str) -> tuple[bytes, str]:
    """Fetch a document from a URL. Returns (bytes, content_type)."""
    import urllib.request
    step(1, f"Fetching document from: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "TermsIQ-POC/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        content_type = resp.headers.get("Content-Type", "")
    print(f"  ✓ Downloaded {len(content):,} bytes | Content-Type: {content_type}")
    return content, content_type


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf, with plain text fallback."""
    try:
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(text)
            if i >= 19:  # cap at 20 pages for POC
                pages.append("\n[... document truncated at 20 pages for POC ...]")
                break
        full_text = "\n".join(pages)
        print(f"  ✓ Extracted {len(full_text):,} characters from {min(len(reader.pages), 20)} pages")
        return full_text
    except Exception:
        # Fallback: treat as plain text (useful for .txt demo files)
        text = pdf_bytes.decode("utf-8", errors="ignore")
        print(f"  ✓ Loaded as plain text: {len(text):,} characters")
        return text


def hash_document(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def preprocess_text(text: str, max_chars: int = 10000) -> str:
    """Truncate and clean document text for LLM submission."""
    # Basic cleanup
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    cleaned = "\n".join(lines)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
        cleaned += "\n[... truncated for POC — production uses intelligent section detection ...]"
    return cleaned


def extract_with_openai(text: str, supplier: str, country: str) -> dict:
    """Call OpenAI GPT-4o to extract the 5 T&C fields."""
    try:
        from openai import OpenAI
    except ImportError:
        print("  ⚠ openai package not installed — pip install openai")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n  ⚠ No OPENAI_API_KEY found in environment.")
        print("  Running in DEMO MODE — returning simulated extraction.\n")
        return _demo_extraction(supplier, country)

    client = OpenAI(api_key=api_key)
    print(f"  Calling GPT-4o (temperature=0)...")

    prompt = EXTRACTION_PROMPT_USER.format(
        supplier=supplier, country=country, text=text
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown fences defensively
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        extracted = json.loads(raw)
        tokens_used = response.usage.total_tokens if response.usage else "unknown"
        print(f"  ✓ Extraction complete | Tokens used: {tokens_used}")
        return extracted
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        print(f"  Raw response: {raw[:300]}")
        return _demo_extraction(supplier, country)


def _demo_extraction(supplier: str, country: str) -> dict:
    """Simulated extraction for demo/testing without API key."""
    print("  [DEMO MODE] Returning simulated extraction result")
    demo_data = {
        "ES": {
            "tpl_amount": {"value": "STATUTORY_MINIMUM", "confidence": "HIGH",
                           "source_text": "Third party liability as required by Spanish law"},
            "grace_period_minutes": {"value": 29, "confidence": "HIGH",
                                     "source_text": "Reservations not collected within 29 minutes will be cancelled"},
            "licence_rules": {"value": "Valid driving licence held for minimum 1 year required. "
                                       "International Driving Permit required for non-EU licences. "
                                       "Minimum age 21.", "confidence": "HIGH",
                              "source_text": "A valid driving licence issued at least 12 months prior"},
            "payment_rules": {"value": "Credit card required for security deposit. "
                                       "Debit cards not accepted for deposit. "
                                       "Prepaid cards not accepted.",
                              "confidence": "HIGH",
                              "source_text": "A valid credit card in the main driver's name is required"},
            "cross_border_conditions": {"value": "Cross-border travel requires prior written authorisation. "
                                                  "Travel to Morocco, Albania, Kosovo prohibited without special permit.",
                                        "confidence": "MEDIUM",
                                        "source_text": "Cross-border travel must be authorised in advance"}
        },
        "DE": {
            "tpl_amount": {"value": "STATUTORY_MINIMUM", "confidence": "HIGH",
                           "source_text": "Haftpflichtversicherung gemäß gesetzlicher Mindestdeckung"},
            "grace_period_minutes": {"value": 60, "confidence": "MEDIUM",
                                     "source_text": "Fahrzeug wird nach angemessener Wartezeit vergeben"},
            "licence_rules": {"value": "German or EU/EEA licence accepted. Non-EU licences require "
                                       "certified German translation. Digital and photocopied licences not accepted.",
                              "confidence": "HIGH",
                              "source_text": "Führerscheine in nicht-lateinischer Schrift erfordern eine beglaubigte Übersetzung"},
            "payment_rules": {"value": "Credit card mandatory for deposit. Debit cards (EC-Karte) "
                                       "not accepted for security deposit.",
                              "confidence": "HIGH",
                              "source_text": "Kreditkarte auf den Namen des Hauptfahrers erforderlich"},
            "cross_border_conditions": {"value": "Cross-border travel within EU permitted. "
                                                  "Travel outside EU (e.g. Switzerland, Turkey) requires advance approval.",
                                        "confidence": "MEDIUM",
                                        "source_text": "Grenzüberschreitende Fahrten außerhalb der EU sind genehmigungspflichtig"}
        }
    }
    return demo_data.get(country, demo_data["ES"])


def validate_extraction(fields: dict) -> dict:
    """Apply validation rules and score confidence."""
    validation_flags = []
    low_confidence_fields = []

    # Grace period range check
    gp = fields.get("grace_period_minutes", {})
    if gp.get("value") is not None:
        try:
            gp_val = int(gp["value"])
            if gp_val < 0 or gp_val > 480:
                validation_flags.append("grace_period_out_of_range")
                fields["grace_period_minutes"]["confidence"] = "LOW"
        except (ValueError, TypeError):
            validation_flags.append("grace_period_not_numeric")
            fields["grace_period_minutes"]["confidence"] = "LOW"

    # Count low confidence fields
    for field_name, field_data in fields.items():
        if isinstance(field_data, dict) and field_data.get("confidence") == "LOW":
            low_confidence_fields.append(field_name)

    overall = (
        "HIGH" if len(low_confidence_fields) == 0 else
        "MEDIUM" if len(low_confidence_fields) <= 2 else
        "LOW"
    )

    requires_review = len(low_confidence_fields) >= 2 or len(validation_flags) > 0
    tpl_needs_cob = (
        fields.get("tpl_amount", {}).get("value") in ["STATUTORY_MINIMUM", None]
    )

    return {
        "overall_confidence": overall,
        "requires_human_review": requires_review,
        "low_confidence_fields": low_confidence_fields,
        "validation_flags": validation_flags,
        "tpl_needs_cob_lookup": tpl_needs_cob,
    }


def cob_lookup(country: str) -> dict:
    """Look up statutory minimum TPL from COB 2026 table."""
    cob = COB_2026.get(country.upper())
    if not cob or cob["confidence"] == "NONE":
        return {
            "value": None,
            "confidence": "NONE",
            "source": "COB Minimum Amount of Coverage 2026",
            "source_url": "https://www.cobx.org/sites/default/files/2026-04/MinimumAmountOfCoverage%202026.pdf",
            "disclaimer": "No COB data available for this country — manual verification required.",
            "note": cob.get("note", "Country not in COB dataset") if cob else "Country not in COB dataset",
            "resolution_method": "COB_LOOKUP",
        }
    return {
        "value": f"Personal injury: {cob['personal_injury']} | Property damage: {cob.get('property_damage', 'N/A')}",
        "confidence": cob["confidence"],
        "source": f"COB Minimum Amount of Coverage 2026 (data date: {cob['data_date']})",
        "source_url": "https://www.cobx.org/sites/default/files/2026-04/MinimumAmountOfCoverage%202026.pdf",
        "disclaimer": "Figures provided for information only. COB assumes no responsibility for accuracy or future changes.",
        "note": cob.get("note"),
        "resolution_method": "COB_LOOKUP",
    }


def build_api_record(supplier, country, source_url, doc_hash,
                     ingested_at, fields, scores) -> dict:
    """Assemble the final API-ready record."""
    return {
        "record_id": f"{supplier}-{country}-{int(datetime.now().timestamp())}",
        "supplier": supplier,
        "pickup_country": country,
        "source_url": source_url,
        "document_hash": doc_hash,
        "ingested_at": ingested_at,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "extraction_model": "gpt-4o",
        "overall_confidence": scores["overall_confidence"],
        "requires_human_review": scores["requires_human_review"],
        "low_confidence_fields": scores["low_confidence_fields"],
        "validation_flags": scores["validation_flags"],
        "status": "PENDING_REVIEW" if scores["requires_human_review"] else "APPROVED_AUTO",
        "fields": fields,
        "api_metadata": {
            "extraction_method": "AI",
            "model_provider": "OpenAI GPT-4o",
            "data_disclaimer": "T&C data is AI-extracted from supplier documents. "
                               "Verify critical information with the supplier directly.",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    }


def print_record_summary(record: dict):
    """Pretty-print the key results."""
    banner("EXTRACTION RESULT")
    print(f"  Supplier:          {record['supplier']}")
    print(f"  Pickup Country:    {record['pickup_country']}")
    print(f"  Overall Confidence:{record['overall_confidence']}")
    print(f"  Status:            {record['status']}")
    if record['requires_human_review']:
        print(f"  ⚠ HUMAN REVIEW REQUIRED")
        print(f"  Low confidence: {', '.join(record['low_confidence_fields'])}")
    if record['validation_flags']:
        print(f"  ⚠ Validation flags: {', '.join(record['validation_flags'])}")

    print(f"\n  {'─'*55}")
    print(f"  EXTRACTED FIELDS:")
    print(f"  {'─'*55}")
    for field_name, field_data in record['fields'].items():
        if isinstance(field_data, dict):
            conf = field_data.get('confidence', '?')
            val  = field_data.get('value', 'null')
            conf_icon = "✓" if conf == "HIGH" else "~" if conf == "MEDIUM" else "✗"
            print(f"\n  [{conf_icon}] {field_name.upper()} (confidence: {conf})")
            if val:
                wrapped = textwrap.fill(str(val), width=55, initial_indent="      ",
                                        subsequent_indent="      ")
                print(wrapped)
            else:
                print("      null / not found")
            if field_data.get('source_text'):
                src = field_data['source_text'][:80]
                print(f"      Source: \"{src}\"")
            if field_data.get('note'):
                print(f"      Note: {field_data['note']}")
            if field_data.get('disclaimer'):
                print(f"      ⚠ {field_data['disclaimer'][:80]}")


def main():
    parser = argparse.ArgumentParser(description="TermsIQ POC — T&C Extraction Pipeline")
    parser.add_argument("--supplier", default="Hertz", help="Supplier name")
    parser.add_argument("--country", default="ES", help="ISO pickup country code (e.g. ES, DE, IT)")
    parser.add_argument("--url", default="https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf",
                        help="URL of the supplier T&C document")
    parser.add_argument("--local-file", default=None, help="Path to a local PDF file")
    parser.add_argument("--output", default="termsiq_output.json", help="Output JSON file path")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode without API key")
    args = parser.parse_args()

    if args.demo:
        os.environ.pop("OPENAI_API_KEY", None)  # force demo mode

    banner(f"TermsIQ POC — {args.supplier} / {args.country}")
    ingested_at = datetime.now(timezone.utc).isoformat()

    # ── Step 1: Fetch or load document ──────────────────────────────────────
    if args.local_file:
        step(1, f"Loading local file: {args.local_file}")
        with open(args.local_file, "rb") as f:
            doc_bytes = f.read()
        source_url = f"local://{args.local_file}"
        print(f"  ✓ Loaded {len(doc_bytes):,} bytes")
    else:
        doc_bytes, _ = fetch_document(args.url)
        source_url = args.url

    # ── Step 2: Extract text ─────────────────────────────────────────────────
    step(2, "Extracting text from document")
    raw_text = extract_text_from_pdf(doc_bytes)
    doc_hash = hash_document(doc_bytes)
    print(f"  ✓ Document hash (MD5): {doc_hash}")

    # ── Step 3: Pre-process ──────────────────────────────────────────────────
    step(3, "Pre-processing text for LLM submission")
    processed_text = preprocess_text(raw_text, max_chars=10000)
    print(f"  ✓ Processed text: {len(processed_text):,} characters")

    # ── Step 4: LLM extraction ───────────────────────────────────────────────
    step(4, f"Extracting T&C fields via OpenAI GPT-4o")
    fields = extract_with_openai(processed_text, args.supplier, args.country)

    # ── Step 5: Validate & score ─────────────────────────────────────────────
    step(5, "Validating extraction and scoring confidence")
    scores = validate_extraction(fields)
    print(f"  ✓ Overall confidence: {scores['overall_confidence']}")
    print(f"  ✓ Requires human review: {scores['requires_human_review']}")
    if scores["low_confidence_fields"]:
        print(f"  ⚠ Low confidence: {', '.join(scores['low_confidence_fields'])}")

    # ── Step 6: COB lookup (if needed) ───────────────────────────────────────
    if scores["tpl_needs_cob_lookup"]:
        step(6, f"TPL not explicit — performing COB 2026 lookup for country: {args.country}")
        cob_result = cob_lookup(args.country)
        fields["tpl_amount"] = {**fields.get("tpl_amount", {}), **cob_result}
        print(f"  ✓ COB result: {cob_result['value'] or 'No data'} (confidence: {cob_result['confidence']})")
    else:
        step(6, "TPL stated explicitly in document — COB lookup not required")

    # ── Step 7: Build final record ───────────────────────────────────────────
    step(7, "Building API-ready output record")
    record = build_api_record(
        supplier=args.supplier,
        country=args.country,
        source_url=source_url,
        doc_hash=doc_hash,
        ingested_at=ingested_at,
        fields=fields,
        scores=scores,
    )

    # ── Step 8: Output ───────────────────────────────────────────────────────
    step(8, f"Writing output to {args.output}")
    with open(args.output, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: {args.output}")

    # ── Print summary ────────────────────────────────────────────────────────
    print_record_summary(record)

    banner("POC COMPLETE")
    print(f"  Full JSON output: {args.output}")
    print(f"  Human review required: {'YES ⚠' if record['requires_human_review'] else 'NO ✓'}")
    print()


if __name__ == "__main__":
    main()
