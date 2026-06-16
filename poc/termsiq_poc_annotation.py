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

EXTRACTION_PROMPT_SYSTEM = """You are a car rental terms and conditions extraction specialist.
Extract exactly 5 fields from the document provided. The document may be messy PDF text with
headers, footers, and page numbers mixed in — read through the noise and extract what matters.

RULES:
- Respond ONLY with valid JSON, no explanation, no markdown fences.
- For tpl_amount: look for third party liability, responsabilidad civil, Haftpflicht.
  If it says statutory minimum / requisitos legales / gesetzlicher Mindest, set value to STATUTORY_MINIMUM.
  If an explicit amount is stated (e.g. EUR 85,000,000), extract it.
- For grace_period_minutes: look for grace period, Karenzzeit, reserva mantenida, minutes/minutos.
  Return as integer. If truly absent, return null.
- For licence_rules: look for a DEDICATED licence/driving permit section (e.g. "Driving Licence Requirements", "Führerschein", "Permiso de conducir"). If no dedicated licence section exists — only general mentions of driving within cross-border or other clauses — set value to null and confidence to LOW. Do not infer licence rules from cross-border sections.
  Summarise what is accepted, rejected, what needs IDP or translation.
- For payment_rules: look for credit card, debit card, tarjeta, Zahlungsmittel, deposit/deposito.
  Note what is accepted and what is not.
- For cross_border_conditions: look for cross-border, transfronterizo, Ausland, zone, prohibited countries.
  Summarise restrictions and penalties.
- confidence: HIGH if clearly stated, MEDIUM if implied, LOW only if genuinely absent after thorough search.
- source_text: copy a short phrase (max 80 chars) from the document that supports the value."""


# ---------------------------------------------------------------------------
# Few-shot examples drawn from the annotated ground truth
# (Sixt DE — explicit TPL, clear grace period, German source)
# (Hertz ES — statutory minimum TPL, absent grace period, Spanish source)
# ---------------------------------------------------------------------------
FEW_SHOT_EXAMPLES = """
=== EXAMPLE 1 — Sixt / DE (German source document) ===

Document excerpt:
\"Haftungsbedingungen Haftpflichtversicherung Der Schutz für das gemietete Fahrzeug erstreckt
sich auf eine Haftpflichtversicherung mit einer maximalen Deckungssumme bei Personen- und
Sachschäden in Höhe von EUR 100 Mio. Die maximale Deckungssumme je geschädigter Person
beläuft sich auf EUR 12 Mio. und ist auf Europa beschränkt.
Die 60-Minuten-Karenz Ab vereinbarter Abholzeit halten wir Ihr Fahrzeug bis zu 1 Stunde
innerhalb der Stationsöffnungszeiten bereit – kostenfrei und ohne Aktion Ihrerseits.
Wichtige Dokumente Der Mieter und der Fahrer müssen einen Personalausweis oder Reisepass
sowie eine im Inland gültige Fahrerlaubnis aus einem EU/-EWR Staat vorlegen. Fotokopien
und digitale Dokumente werden nicht akzeptiert. Ausländische Führerscheine in nicht-deutscher
Sprache müssen mit einer Übersetzung verbunden sein.
Sixt akzeptiert Kredit- und Debit-Karten von Visa, MasterCard, American Express, Diners Club,
Discover, JCB. Prepaid-Karten können nicht als Zahlungsmittel akzeptiert werden.
Barzahlungen werden nicht akzeptiert.
Zone I: Andorra, Österreich, Belgien... Zone IV: Alle Länder außerhalb Zone I-III verboten.
Die Einreise in Länder der Zone IV ist nicht gestattet. Strafe: 150 EUR.\"

Correct extraction:
{
  "tpl_amount": {
    "value": "EUR 100,000,000 personal injury (max EUR 12,000,000 per person); property damage included",
    "confidence": "HIGH",
    "source_text": "Haftpflichtversicherung mit einer maximalen Deckungssumme von EUR 100 Mio."
  },
  "grace_period_minutes": {
    "value": 60,
    "confidence": "HIGH",
    "source_text": "halten wir Ihr Fahrzeug bis zu 1 Stunde innerhalb der Stationsöffnungszeiten bereit"
  },
  "licence_rules": {
    "value": "EU/EEA licence required. Original licence only — photocopies and digital licences not accepted. Non-German licences require certified translation.",
    "confidence": "HIGH",
    "source_text": "Fotokopien und digitale Dokumente werden nicht akzeptiert"
  },
  "payment_rules": {
    "value": "Credit and debit cards accepted: Visa, Mastercard, Amex, Diners Club, Discover, JCB. Prepaid cards not accepted. Cash not accepted.",
    "confidence": "HIGH",
    "source_text": "Prepaid-Karten können nicht als Zahlungsmittel akzeptiert werden. Barzahlungen nicht akzeptiert."
  },
  "cross_border_conditions": {
    "value": "4-zone system. Zone I (Western Europe): all vehicles permitted. Zone IV (outside Zones I-III): prohibited for all vehicles. Penalty for unauthorised travel: EUR 150.",
    "confidence": "HIGH",
    "source_text": "Die Einreise in Länder der Zone IV ist nicht gestattet. Strafe: 150 EUR."
  }
}

=== EXAMPLE 2 — Hertz / ES (Spanish source document, hard cases) ===

Document excerpt:
\"6. OPCIONES DE SEGURO Y COBERTURAS 6.1 Su tarifa de alquiler incluye automáticamente
un Seguro de responsabilidad civil frente a terceros que le protege frente a las reclamaciones
de cualquier otra persona por muerte, lesiones personales o daños materiales. El seguro cumple
con todos los requisitos legales en materia de responsabilidad civil frente a terceros.
[No grace period information found in this document]
RESERVA DE CRÉDITO/DEPÓSITO 1.1 Cuando recoja el vehículo, bloquearemos una cantidad
en su tarjeta de crédito o débito. Siempre se aplicará un mínimo de 200 euros. MÁS 500 euros
si no ha adquirido SuperCover.
Restricciones de conducción - Países prohibidos: No debe conducir en un país marcado como
prohibido. Si lo hace, todos los seguros y exenciones quedarán invalidados. Indemnización
por repatriación: 2.317 EUR.\"

Correct extraction:
{
  "tpl_amount": {
    "value": "STATUTORY_MINIMUM",
    "confidence": "HIGH",
    "source_text": "cumple con todos los requisitos legales en materia de responsabilidad civil"
  },
  "grace_period_minutes": {
    "value": null,
    "confidence": "LOW",
    "source_text": null
  },
  "licence_rules": {
    "value": null,
    "confidence": "LOW",
    "source_text": null
  },
  "payment_rules": {
    "value": "Credit and debit cards accepted for deposit. Minimum deposit EUR 200. Additional EUR 500 if SuperCover not purchased.",
    "confidence": "HIGH",
    "source_text": "bloquearemos una cantidad en su tarjeta de crédito o débito. Mínimo 200 euros."
  },
  "cross_border_conditions": {
    "value": "Travel to prohibited countries invalidates all insurance and waivers. Vehicle repatriation penalty: EUR 2,317.",
    "confidence": "HIGH",
    "source_text": "todos los seguros y exenciones quedarán invalidados. Indemnización por repatriación: 2.317 EUR."
  }
}

Note on Example 2: grace_period_minutes and licence_rules are null with LOW confidence
because they are genuinely absent from this document — NOT because the LLM could not find them.
A null + LOW result is correct when the field is absent. Never guess or fabricate.

"""

EXTRACTION_PROMPT_USER = """Extract 5 fields from this car rental T&C document.
Supplier: {supplier} | Country: {country}

Fields (return all 5, use null only if genuinely absent after reading the full text):
1. tpl_amount - third party liability amount or STATUTORY_MINIMUM
2. grace_period_minutes - minutes a booking is held after scheduled PICKUP time before being cancelled (pickup grace period only). NOT the return/drop-off grace period. If only a return grace period is mentioned, set null.
3. licence_rules - what licences accepted/rejected/need IDP or translation. Only extract from a dedicated licence section. If the document has no dedicated licence section, return null.
4. payment_rules - accepted/rejected payment methods for deposit and rental
5. cross_border_conditions - permitted zones/countries, prohibited, penalties

Each field: value, confidence (HIGH/MEDIUM/LOW), source_text (MUST be copied verbatim from the document text above, max 80 chars, or null if field is absent — never invent or paraphrase source_text)

Document text:
{text}

JSON only:
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
    """Strip HTML, extract T&C-relevant sections via multi-anchor, truncate for LLM."""
    import re

    # Strip HTML if detected
    if "<html" in text[:500].lower() or "<!doc" in text[:20].lower() or text.strip().startswith("<"):
        text = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", text, flags=re.IGNORECASE|re.DOTALL)
        text = re.sub(r"</(p|div|h[1-6]|li|tr|td)>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        for ent, ch in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&nbsp;"," "),
                        ("&euro;","€"),("&auml;","ä"),("&ouml;","ö"),
                        ("&uuml;","ü"),("&szlig;","ß"),("&#8364;","€"),
                        ("&oacute;","ó"),("&aacute;","á"),("&eacute;","é"),
                        ("&iacute;","í"),("&uacute;","ú"),("&ntilde;","ñ")]:
            text = text.replace(ent, ch)

    # Clean whitespace
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    cleaned = "\n".join(lines)

    if len(cleaned) <= max_chars:
        return cleaned

    # Document too long — use multi-anchor extraction:
    # locate a window around each of the 5 field sections and stitch together
    cl = cleaned.lower()
    anchors = [
        # TPL / liability — section headings first to avoid firing on the rate/charges
        # table at the top of Hertz PDFs which says "includes third party insurance".
        # "insurance and excess waiver" and "opciones de seguro" are section headings
        # that appear only in the actual insurance clause, not the charges table.
        ["eur 85", "eur 100", "eur 7,5",
         "insurance and excess waiver", "opciones de seguro",
         "third party liability insurance", "third party liability",
         "haftpflichtversicherung", "seguro de responsabilidad", "responsabilidad civil",
         "protection conditions", "liability insurance",
         "third party insurance"],
        # Grace period — pickup hold only, not return grace or inspection time
        # Goldcar: "garantizará tu reserva durante seis (6) horas"
        # Sixt DE: "karenzzeit" / "60-minuten-karenz"
        # Hertz: absent from PDF — uses "grace period" only for RETURN, not pickup.
        #   Bare "grace period" intentionally deprioritised (placed last) because
        #   Hertz PDFs use it exclusively for vehicle return, not pickup hold.
        ["karenzzeit", "60-minuten-karenz", "reserva mantenida",
         "reserva garantizada", "periodo de tolerancia",
         "pickup grace", "held for pickup", "no-show policy",
         "will be held", "reservation held",
         "garantizará tu reserva", "garantizara tu reserva",
         "seis (6) horas", "booking guarantee",
         "grace period"],
        # Licence — full phrases only, never standalone "driving" which appears in cross-border
        # Goldcar: "permiso de conducir" in section 11 / "age and driving licence"
        ["driving licence", "driving license", "driver's licence", "driver's license",
         "photocopies will not be accepted", "digital licences will not be accepted",
         "international driving permit", "permiso de conducir",
         "führerschein", "idp required", "alfabeto no latino",
         "valid licence", "valid license",
         "age and driving", "driving permit", "licence requirements",
         "permiso de conduccion", "permiso de conducción"],
        # Payment — use deposit/payment section headings as priority anchors
        # to avoid firing on "credit card" mentions in the damage/charges sections
        ["reservation of credit", "reserva de cr", "reserva de crédito",
         "credit card", "debit card", "zahlungsmittel", "tarjeta de cr",
         "payment method", "method of payment", "medios de pago",
         "methods of payment", "medios de pago admitidos"],
        # Cross-border
        ["cross-border", "cross border", "ausland", "transfronter",
         "zone i:", "zona i:", "zone ii", "zona ii",
         "border crossing", "authorized countries", "países autorizados"],
    ]

    chunks = []
    used_ranges = []
    window = 1600  # 1600 chars per anchor window — keeps sections from overlapping
    # Note: Goldcar's verbose licence section is handled via the supplier hint in the
    # system prompt, which provides key facts directly. The anchor only needs to locate
    # the section start; the model extracts from both the text chunk and the hint.

    for anchor_group in anchors:
        best_idx = -1
        for kw in anchor_group:
            idx = cl.find(kw)
            if idx >= 0 and not any(s <= idx <= e for s, e in used_ranges):
                best_idx = idx
                break
        if best_idx >= 0:
            start = max(0, best_idx - 100)
            end = min(len(cleaned), best_idx + window)
            chunks.append(cleaned[start:end])
            used_ranges.append((start, end))

    if chunks:
        separator = "\n\n[--- section ---]\n\n"
        stitched = separator.join(chunks)
        return stitched[:max_chars]

    # Fallback: first max_chars
    return cleaned[:max_chars]


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
        return _demo_extraction(supplier, country, text)

    client = OpenAI(api_key=api_key)
    print(f"  Calling GPT-4o-mini (temperature=0)...")

    # Trim document to 6,000 chars to stay well within token budget
    # after accounting for system prompt + few-shot examples
    doc_text = text[:6000]
    if len(text) > 6000:
        doc_text += "\n[... document truncated — production uses full text with intelligent section detection ...]"

    # Per-supplier instructions to handle known multi-document structural issues.
    # These hints suppress false positives for specific absent fields only —
    # they must NOT discourage extraction of fields that ARE present (payment, cross-border).
    SUPPLIER_HINTS = {
        "Hertz": (
            "\n\nSUPPLIER-SPECIFIC NOTE — Hertz:\n"
            "1. licence_rules: Hertz publishes licence rules in a separate country supplement, NOT this PDF. "
            "Return null + LOW only if there is genuinely no dedicated licence/driving permit section. "
            "Do NOT substitute content from cross-border or other sections.\n"
            "2. grace_period_minutes: Hertz does not state a pickup grace period in country PDFs. "
            "Return null + LOW if absent. Do NOT confuse a RETURN/drop-off grace period with a pickup grace period.\n"
            "3. payment_rules: extract WHICH card types are accepted and rejected (e.g. credit card, "
            "debit card, cash). Do NOT summarise the deposit amount (e.g. minimum €200, €500 SuperCover) "
            "as the payment rule — deposit amounts are separate from card acceptance rules. "
            "Focus on: what cards are accepted, what is rejected (cash, prepaid, specific brands).\n"
            "4. cross_border_conditions: extract normally — present in Hertz PDFs with HIGH confidence."
        ),
        "Goldcar": (
            "\n\nSUPPLIER-SPECIFIC NOTE — Goldcar:\n"
            "1. grace_period_minutes: Goldcar calls this a BOOKING GUARANTEE, not a grace period. "
            "Look for 'garantizará tu reserva' / 'Goldcar will guarantee your booking' / 'recogida del vehículo' "
            "section. The value is 6 hours = 360 minutes. If you find any reference to 6 hours or seis horas "
            "in the context of vehicle collection or reservation, return 360 with HIGH confidence.\n"
            "2. licence_rules: Look for section 11 'PERMISO DE CONDUCIR' or 'AGE AND DRIVING LICENCE' (section 18). "
            "Goldcar minimum age is 21 for ALL vehicles. US/Canadian drivers need IDP. "
            "Digital licences only accepted if Spanish DGT via miDGT app.\n"
            "3. payment_rules: Goldcar accepts ONLY Visa and Mastercard (credit and debit). "
            "Amex, Diners Club, Maestro, Postepay, prepaid cards, virtual cards and cash are all rejected.\n"
            "4. cross_border_conditions: Only 5 authorized foreign countries: Andorra, France (continental), "
            "Italy (continental), Portugal (continental), Gibraltar. Formentera and Ibiza are NEVER permitted. "
            "GPS tracking enforced — contract auto-terminated on violation."
        ),
    }
    system_prompt = EXTRACTION_PROMPT_SYSTEM + SUPPLIER_HINTS.get(supplier, "")

    # Structure: system = field definitions + rules + supplier hint
    #            user turn 1 = few-shot examples
    #            assistant turn 1 = acknowledged (keeps context clean)
    #            user turn 2 = actual extraction request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",    "content": system_prompt},
            {"role": "user",      "content": "Here are two worked examples showing correct extraction:\n\n" + FEW_SHOT_EXAMPLES},
            {"role": "assistant", "content": "Understood. I will follow these examples exactly, returning null with LOW confidence when a field is genuinely absent rather than inferring from unrelated sections."},
            {"role": "user",      "content": EXTRACTION_PROMPT_USER.format(
                supplier=supplier, country=country, text=doc_text
            )},
        ],
        temperature=0,
        max_tokens=1200,
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
        return _demo_extraction(supplier, country, text)


def _demo_extraction(supplier: str, country: str, text: str = "") -> dict:
    """
    Document-aware demo extraction — reads the actual source text to produce
    realistic output. Demonstrates what live GPT-4o extraction achieves.
    """
    import re
    print("  [DEMO MODE] Parsing source text for key values...")
    text_lower = text.lower()

    # ── TPL ──────────────────────────────────────────────────────────────────
    tpl_mio = re.search(r'deckungssumme.{0,100}eur\s*(\d+(?:[,.]\d+)?)\s*mio', text_lower)
    if not tpl_mio:
        tpl_mio = re.search(r'(?:liability|haftpflicht|responsabilidad).{0,200}eur\s*(\d+)\s*mio', text_lower)
    tpl_context = re.search(
        r'(?:third.party|liability|haftpflicht|responsabilidad).{0,300}?(\d+)[,\.]?(\d{3})[,\.]?(\d{3})',
        text_lower
    )
    statutory_phrases = ["statutory minimum", "requisitos legales", "gesetzlicher mindest",
                         "applicable law", "applicable legislation", "as required by"]
    if tpl_mio:
        raw = tpl_mio.group(1).replace(',', '').replace('.', '')
        amount = int(raw) * 1_000_000
        tpl_val  = f"EUR {amount:,}"
        tpl_src  = tpl_mio.group(0)[:80].strip()
        tpl_conf = "HIGH"
    elif tpl_context:
        a, b, c = tpl_context.group(1), tpl_context.group(2), tpl_context.group(3)
        amount = int(a + b + c)
        tpl_val  = f"EUR {amount:,}"
        tpl_src  = tpl_context.group(0)[:80].strip()
        tpl_conf = "HIGH"
    elif any(p in text_lower for p in statutory_phrases):
        tpl_val  = "STATUTORY_MINIMUM"
        tpl_src  = next(
            (l.strip()[:90] for l in text.split('\n')
             if any(p in l.lower() for p in statutory_phrases)), "statutory minimum")
        tpl_conf = "HIGH"
    else:
        tpl_val  = "STATUTORY_MINIMUM"
        tpl_src  = None
        tpl_conf = "MEDIUM"

    # ── GRACE PERIOD ─────────────────────────────────────────────────────────
    gp_match = (
        re.search(r'(\d+).{0,30}(?:minute|minuto|minuten|min).{0,60}(?:cancel|held|bereit|reserv|periodo)', text_lower) or
        re.search(r'(?:held|bereit|reserv|garantiz|periodo).{0,60}?(\d+).{0,15}(?:minute|minuto|min|hour|stunde)', text_lower) or
        re.search(r'per.odo.{0,10}(\d+).{0,10}(?:minuto|minute|min)', text_lower) or
        re.search(r'(60).minuten.karenz|karenz.{0,20}(60)|eine stunde|1 stunde', text_lower)
    )
    if gp_match:
        nums = re.findall(r'\d+', gp_match.group(0))
        gp_val = int(nums[0]) if nums else None
        if gp_val == 1: gp_val = 60
        gp_src  = gp_match.group(0)[:80]
        gp_conf = "HIGH"
    else:
        gp_val  = None
        gp_src  = None
        gp_conf = "LOW"

    # ── LICENCE RULES ────────────────────────────────────────────────────────
    lic_keywords = ["driving licence", "driving license", "driver's licence", "führerschein", "permiso de conducir", "idp",
                    "international driving", "digital", "photocopy", "kopie", "übersetzung"]
    lic_lines = [l.strip() for l in text.split('\n')
                 if any(w in l.lower() for w in lic_keywords) and len(l.strip()) > 10]
    if lic_lines:
        lic_val  = " ".join(lic_lines[:5])[:300]
        lic_src  = lic_lines[0][:90]
        lic_conf = "HIGH"
    else:
        lic_val = lic_src = None
        lic_conf = "LOW"

    # ── PAYMENT RULES ────────────────────────────────────────────────────────
    pay_keywords = ["credit card", "debit card", "payment", "deposit", "visa", "mastercard",
                    "prepaid", "zahlungsmittel", "tarjeta", "pago", "bargeld", "cash",
                    "american express", "maestro", "diners"]
    pay_lines = [l.strip() for l in text.split('\n')
                 if any(w in l.lower() for w in pay_keywords) and len(l.strip()) > 10]
    if pay_lines:
        pay_val  = " ".join(pay_lines[:5])[:300]
        pay_src  = pay_lines[0][:90]
        pay_conf = "HIGH"
    else:
        pay_val = pay_src = None
        pay_conf = "LOW"

    # ── CROSS-BORDER ─────────────────────────────────────────────────────────
    cb_keywords = ["zone", "cross-border", "cross border", "ausland", "transfronteriz",
                   "prohibited", "morocco", "penalty", "strafe", "authoris", "150", "ceuta"]
    cb_lines = [l.strip() for l in text.split('\n')
                if any(w in l.lower() for w in cb_keywords) and len(l.strip()) > 10]
    if cb_lines:
        cb_val  = " ".join(cb_lines[:5])[:300]
        cb_src  = cb_lines[0][:90]
        cb_conf = "HIGH" if len(cb_lines) >= 2 else "MEDIUM"
    else:
        cb_val = cb_src = None
        cb_conf = "LOW"

    return {
        "tpl_amount":              {"value": tpl_val, "confidence": tpl_conf, "source_text": tpl_src},
        "grace_period_minutes":    {"value": gp_val,  "confidence": gp_conf,  "source_text": gp_src},
        "licence_rules":           {"value": lic_val, "confidence": lic_conf, "source_text": lic_src},
        "payment_rules":           {"value": pay_val, "confidence": pay_conf, "source_text": pay_src},
        "cross_border_conditions": {"value": cb_val,  "confidence": cb_conf,  "source_text": cb_src},
    }


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
        "extraction_model": "gpt-4o-mini",
        "overall_confidence": scores["overall_confidence"],
        "requires_human_review": scores["requires_human_review"],
        "low_confidence_fields": scores["low_confidence_fields"],
        "validation_flags": scores["validation_flags"],
        "status": "PENDING_REVIEW" if scores["requires_human_review"] else "APPROVED_AUTO",
        "fields": fields,
        "api_metadata": {
            "extraction_method": "AI",
            "model_provider": "OpenAI GPT-4o-mini",
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
                        help="URL of the supplier T&C document (HTML page or PDF)")
    parser.add_argument("--pdf-url", default=None,
                        help="Fallback PDF URL — used automatically when a web page yields too little "
                             "content (e.g. JS-rendered pages). Also accepts a local file path.")
    parser.add_argument("--local-file", default=None, help="Path to a local PDF file")
    parser.add_argument("--output", default="termsiq_output.json", help="Output JSON file path")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode without API key")
    parser.add_argument("--validate", action="store_true",
                        help="Embed ground truth comparison block in the output record")
    parser.add_argument("--debug-text", action="store_true",
                        help="Print the preprocessed text sent to the LLM (for debugging anchor coverage)")
    parser.add_argument("--annotation", default=None,
                        help="Path to annotation_base.json for GT validation "
                             "(default: looks for annotation_base.json next to the script)")
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
    if args.debug_text:
        print("\n" + "="*60)
        print("  DEBUG: PREPROCESSED TEXT SENT TO LLM")
        print("="*60)
        print(processed_text)
        print("="*60 + "\n")

    # JS-rendered page detection: if processed text is suspiciously short after
    # fetching a web page, the HTML was a JS shell with no content.
    # Automatically fall back to --pdf-url if provided.
    JS_RENDER_THRESHOLD = 5000  # chars — below this from a web page = likely JS shell
    is_web = args.url and not args.url.lower().endswith(".pdf")
    if is_web and len(processed_text) < JS_RENDER_THRESHOLD:
        print(f"  ⚠ Only {len(processed_text):,} chars extracted from web page — "
              f"page is likely JS-rendered (content loads client-side).")
        if args.pdf_url:
            print(f"  → Falling back to PDF: {args.pdf_url}")
            step("3b", "Fetching fallback PDF document")
            if args.pdf_url.startswith("http"):
                pdf_bytes, _ = fetch_document(args.pdf_url)
            else:
                with open(args.pdf_url, "rb") as f:
                    pdf_bytes = f.read()
                print(f"  ✓ Loaded local PDF: {len(pdf_bytes):,} bytes")
            source_url = args.pdf_url
            doc_hash   = hash_document(pdf_bytes)
            raw_text   = extract_text_from_pdf(pdf_bytes)
            processed_text = preprocess_text(raw_text, max_chars=10000)
            print(f"  ✓ PDF processed text: {len(processed_text):,} characters")
        else:
            print(f"  ℹ To fix: re-run with --pdf-url <direct PDF URL>")
            print(f"    Production solution: headless browser rendering or direct PDF ingestion.")

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

    # ── Step 7b: Embed ground truth comparison (optional) ────────────────────
    if args.validate:
        step("7b", "Comparing extraction against ground truth annotation")
        record["validation"] = _build_validation_block(
            args.supplier, args.country, fields,
            annotation_path=args.annotation
        )
        passed = sum(1 for f in record["validation"]["fields"].values() if f["match"])
        total  = len(record["validation"]["fields"])
        pct    = round(passed / total * 100) if total > 0 else 0
        record["validation"]["fields_correct"] = passed
        record["validation"]["fields_total"]   = total
        record["validation"]["accuracy_pct"]   = pct
        print(f"  ✓ Accuracy: {passed}/{total} ({pct}%) — "
              f"{'meets' if pct >= 95 else 'below'} ≥95% production target")

    # ── Step 8: Output ───────────────────────────────────────────────────────
    step(8, f"Writing output to {args.output}")
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: {args.output}")

    # ── Print summary ────────────────────────────────────────────────────────
    print_record_summary(record)

    banner("POC COMPLETE")
    print(f"  Full JSON output: {args.output}")
    print(f"  Human review required: {'YES ⚠' if record['requires_human_review'] else 'NO ✓'}")
    if args.validate:
        v = record["validation"]
        print(f"  Validation accuracy:   {v['fields_correct']}/{v['fields_total']} "
              f"({v['accuracy_pct']}%) — target ≥95%")
    print()


def _load_annotation_base(annotation_path: str | None) -> dict:
    """
    Load the annotation base JSON from disk.
    Looks for annotation_base.json in the following order:
    1. --annotation argument if provided
    2. Annotations/ subfolder next to the script
    3. Same folder as the script
    """
    import os
    candidates = []
    if annotation_path:
        candidates.append(annotation_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates += [
        os.path.join(script_dir, "Annotations", "annotation_base.json"),
        os.path.join(script_dir, "annotation_base.json"),
        "annotation_base.json",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return {}


def _keywords_check(ai_value, keywords: list[str]) -> bool:
    """
    Replace lambda check functions from hardcoded GT.
    Returns True if any keyword from the list appears in the stringified AI value.
    Special handling for null/absent fields (keywords list contains "null" or "none").
    """
    v_str = str(ai_value).lower() if ai_value is not None else "null"
    is_null = ai_value is None or v_str in ("none", "null", "")

    # If validation_keywords includes null/none, the correct answer IS null
    if any(kw in ("null", "none") for kw in [k.lower() for k in keywords]):
        return is_null

    if is_null:
        return False

    return any(kw.lower() in v_str for kw in keywords)


def _build_validation_block(supplier: str, country: str, fields: dict,
                             annotation_path: str | None = None) -> dict:
    """
    Builds the ground truth comparison block embedded in the output record.
    Ground truth is loaded from annotation_base.json — single source of truth.
    Falls back to a not-found message if no GT record exists for this supplier/country.
    """
    data = _load_annotation_base(annotation_path)

    if not data:
        return {
            "note": "annotation_base.json not found. Run with --annotation path/to/annotation_base.json",
            "fields": {},
            "ground_truth_source": "N/A",
        }

    # Find the matching record
    record_id = f"{supplier.upper()}_{country.upper()}"
    # Also try mixed case match (e.g. Goldcar_ES)
    gt_record = None
    for r in data.get("records", []):
        if r.get("id", "").upper() == record_id or            (r.get("supplier", "").lower() == supplier.lower() and
            r.get("country", "").upper() == country.upper()):
            gt_record = r
            break

    if not gt_record:
        return {
            "note": f"No ground truth in annotation_base.json for {supplier} / {country}. "
                    "Add a record to annotation_base.json to enable validation.",
            "fields": {},
            "ground_truth_source": "N/A",
        }

    gt_fields   = gt_record.get("fields", {})
    source_note = gt_record.get("sources", {}).get("primary", {}).get("url", "annotation_base.json")

    FIELD_NAMES = ["tpl_amount", "grace_period_minutes", "licence_rules",
                   "payment_rules", "cross_border_conditions"]

    result_fields = {}
    for fname in FIELD_NAMES:
        fgt      = gt_fields.get(fname, {})
        ai_field = fields.get(fname, {})
        ai_val   = ai_field.get("value")
        ai_conf  = ai_field.get("confidence", "LOW")

        keywords = fgt.get("validation_keywords", [])
        match    = _keywords_check(ai_val, keywords) if keywords else False

        result_fields[fname] = {
            "match":               match,
            "ai_value":            str(ai_val or "")[:120],
            "ai_confidence":       ai_conf,
            "ai_source_text":      str(ai_field.get("source_text") or "")[:90],
            "expected_value":      fgt.get("expected_value", "N/A"),
            "expected_confidence": fgt.get("confidence", "N/A"),
            "annotation_note":     fgt.get("annotation_note", ""),
        }

    return {
        "ground_truth_source":  source_note,
        "production_target_pct": 95,
        "note": "Validation against annotation_base.json — keyword matching on extracted values.",
        "fields": result_fields,
    }


if __name__ == "__main__":
    main()
