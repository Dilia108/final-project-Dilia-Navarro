"""
TermsIQ — Gradio UI
====================
A web UI over the existing termsiq_mvp.py extraction pipeline. Two ways in:

  - Quick Test: the 5 supplier/country combinations that have verified ground
    truth in annotation_base.json, for a reliable, accuracy-checkable demo.
  - Advanced: any URL or uploaded PDF, for any supplier/country — shows the
    pipeline genuinely generalizing, with no ground truth to compare against.

This file is a presentation layer only. All extraction logic lives in
termsiq_mvp.run_extraction() — nothing here re-implements pipeline behavior,
so a fix made there is automatically reflected here too.

Run with:
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...
    python gradio_app.py
"""

import os
import json
import gradio as gr

import termsiq_mvp


# ── Known, ground-truth-verified test cases ─────────────────────────────────
# Mirrors annotation_base.json's records — kept here as a flat lookup so the
# UI doesn't need to parse the annotation file just to populate a dropdown.
PRESETS = {
    "Hertz — Spain (ES)": {
        "supplier": "Hertz", "country": "ES",
        "url": "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf",
        "pdf_url": None, "needs_local_pdf": False,
    },
    "Hertz — Germany (DE)": {
        "supplier": "Hertz", "country": "DE",
        "url": "https://images.hertz.com/pdfs/RT_FULL_DE_EN.pdf",
        "pdf_url": None, "needs_local_pdf": False,
    },
    "Sixt — Spain (ES)": {
        "supplier": "Sixt", "country": "ES",
        "url": "https://www.sixt.es/php/terms/view?language=en_US&liso=ES&rtar=000&view=EPP&tlang=es_ES&style=typo3",
        "pdf_url": None, "needs_local_pdf": False,
    },
    "Sixt — Germany (DE)": {
        "supplier": "Sixt", "country": "DE",
        "url": "https://www.sixt.de/php/terms/view?language=en_US&liso=DE&rtar=000&view=EPP&tlang=de_DE&style=typo3",
        "pdf_url": None, "needs_local_pdf": False,
    },
    "Goldcar — Spain (ES)": {
        "supplier": "Goldcar", "country": "ES",
        "url": "https://www.goldcar.es/en-gb/terms-and-conditions/",
        "pdf_url": None, "needs_local_pdf": True,
    },
}

# Roughly maps run_extraction()'s step labels to a progress-bar fraction.
# Not every run hits every step (e.g. no secondary source needed), so this
# is approximate by design — good enough for a progress bar, not meant to
# be exact.
STEP_PROGRESS = {
    1: 0.08, 2: 0.18, 3: 0.28, "3b": 0.35, 4: 0.50,
    "4b": 0.60, "4.1": 0.62, "4.2": 0.66, "4.3": 0.70, "4.4": 0.73,
    "4c": 0.78, 5: 0.85, 6: 0.92, 7: 0.96, "7b": 0.99,
}

CONFIDENCE_BADGE = {
    "HIGH": "🟢 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🔴 LOW", "NONE": "⚪ NONE",
}

FIELD_LABELS = {
    "tpl_amount": "TPL Coverage Amount",
    "grace_period_minutes": "Grace Period (minutes)",
    "licence_rules": "Licence Rules",
    "payment_rules": "Payment Rules",
    "cross_border_conditions": "Cross-Border Conditions",
}

FIELD_ORDER = ["tpl_amount", "grace_period_minutes", "licence_rules",
               "payment_rules", "cross_border_conditions"]


PRIMARY_NAVY = "#123458"
ACCENT_TEAL = "#14B8A6"
BG_COLOR = "#F8FAFC"
TEXT_COLOR = "#1E293B"
RISK_RED = "#EF4444"

theme = gr.themes.Base(
    font=gr.themes.GoogleFont("Inter", weights=(400, 500, 600)),
    font_mono=gr.themes.GoogleFont("JetBrains Mono", weights=(400, 500)),
).set(
    body_background_fill=BG_COLOR,
    body_text_color=TEXT_COLOR,
    block_background_fill="#FFFFFF",
    block_border_color="#E2E8F0",
    block_title_text_color=PRIMARY_NAVY,
    block_title_text_weight="600",
    block_label_text_color=TEXT_COLOR,
    body_text_weight="400",
    prose_text_weight="400",
    prose_header_text_weight="600",
    button_primary_background_fill=PRIMARY_NAVY,
    button_primary_background_fill_hover="#1B4A75",
    button_primary_text_color="#FFFFFF",
    button_primary_border_color=PRIMARY_NAVY,
    color_accent=ACCENT_TEAL,
    color_accent_soft=f"{ACCENT_TEAL}1A",
    border_color_accent=ACCENT_TEAL,
    link_text_color=ACCENT_TEAL,
    link_text_color_hover="#0F9488",
    link_text_color_active="#0F9488",
    input_border_color_focus=ACCENT_TEAL,
    checkbox_background_color_selected=ACCENT_TEAL,
    checkbox_border_color_selected=ACCENT_TEAL,
    error_text_color=RISK_RED,
    error_border_color=RISK_RED,
    error_icon_color=RISK_RED,
)

# Custom CSS for things the theme API doesn't expose directly: precise
# heading-weight hierarchy inside rendered markdown (titles=SemiBold 600,
# section headers=Medium 500, body=Regular 400), and a hard kill on italics
# anywhere — belt-and-suspenders alongside removing italics from the content
# itself, in case any component default ever introduces an <em>/<i> tag.
CUSTOM_CSS = f"""
.prose h2 {{ font-weight: 600 !important; color: {PRIMARY_NAVY}; }}
.prose h3 {{ font-weight: 500 !important; color: {TEXT_COLOR}; }}
.prose p, .prose li {{ font-weight: 400; }}
.prose blockquote {{
    border-left: 3px solid {ACCENT_TEAL};
    color: {TEXT_COLOR};
    background: {ACCENT_TEAL}0D;
    padding: 8px 14px;
    border-radius: 4px;
}}
em, i {{ font-style: normal !important; }}
"""


def format_record_as_markdown(record: dict) -> str:
    """Renders an extraction record as readable Markdown — mirrors the CLI's
    print_record_summary(), just formatted for a web view instead of a terminal."""
    lines = []

    conf_badge = CONFIDENCE_BADGE.get(record["overall_confidence"], record["overall_confidence"])

    lines.append(f"## {record['supplier']} — {record['pickup_country']}")
    lines.append(f"Overall confidence: **{conf_badge}**")
    if record.get("low_confidence_fields"):
        lines.append(f"\nLow confidence fields: **{', '.join(record['low_confidence_fields'])}**")
    if record.get("validation_flags"):
        lines.append(f"\n⚠️ Validation flags: **{', '.join(record['validation_flags'])}**")
    lines.append("\n---")

    for fname in FIELD_ORDER:
        fdata = record["fields"].get(fname)
        if not isinstance(fdata, dict):
            continue
        label = FIELD_LABELS.get(fname, fname)
        is_curated = fdata.get("is_curated", False)
        conf = fdata.get("confidence", "?")
        badge = "🔷 SUPPLIER-CURATED (not live-extracted)" if is_curated \
            else CONFIDENCE_BADGE.get(conf, conf)

        lines.append(f"\n### {label}")
        lines.append(f"Confidence: **{badge}**\n")

        val = fdata.get("value")
        if val:
            lines.append(f"**{val}**")
        elif fdata.get("status_message"):
            lines.append(f"ℹ️ {fdata['status_message']}")
        else:
            lines.append("Not found in this document")

        if fdata.get("source_text"):
            lines.append(f"\n> Source: \"{fdata['source_text']}\"")

        if is_curated:
            src_desc = (fdata.get("source") or "").replace("supplier_curated: ", "")
            if src_desc:
                lines.append(f"\nCurated source: {src_desc}")
            if fdata.get("curated_url"):
                lines.append(f"  \nCurated URL: {fdata['curated_url']}")
        elif fdata.get("source") and fdata.get("source") != fdata.get("source_text"):
            lines.append(f"\nReference: {fdata['source']}")
            if fdata.get("source_url"):
                lines.append(f"  \nReference URL: {fdata['source_url']}")

        if fdata.get("note"):
            lines.append(f"\nNote: {fdata['note']}")
        if fdata.get("disclaimer"):
            lines.append(f"\n⚠️ {fdata['disclaimer']}")

    if record.get("validation"):
        v = record["validation"]
        lines.append("\n---\n## Quality Check — vs. Verified Ground Truth")
        if v.get("fields"):
            pct = v.get("accuracy_pct", 0)
            target_note = "meets" if pct >= 95 else "below"
            lines.append(f"Accuracy: **{v['fields_correct']}/{v['fields_total']} ({pct}%)** "
                          f"— {target_note} the ≥95% production target\n")
            for fname in FIELD_ORDER:
                fv = v["fields"].get(fname)
                if not fv:
                    continue
                icon = "✅" if fv["match"] else "❌"
                label = FIELD_LABELS.get(fname, fname)
                lines.append(f"- {icon} **{label}** — expected: `{fv['expected_value']}` "
                              f"| got: `{fv['ai_value'] or 'null'}`")
        else:
            lines.append(v.get("note", "No ground truth available for this combination."))

    if record.get("sources_used") and len(record["sources_used"]) > 1:
        lines.append("\n---\n## Sources Used")
        for s in record["sources_used"]:
            filled = f" → filled: {', '.join(s['fields_filled'])}" if s.get("fields_filled") else ""
            lines.append(f"- **[{s['role']}]** {s['url']}{filled}")

    return "\n".join(lines)


def format_status_banner(record: dict) -> str:
    """A small standalone HTML banner for the status badge — kept separate from
    the main gr.Markdown result so its colors render exactly as specified
    (gr.Markdown sanitizes HTML by default, since real extracted document
    text flows through it; this banner only ever contains fixed strings from
    our own code, never document content, so it's safe to style directly)."""
    is_approved = record["status"] == "APPROVED_AUTO"
    color = "#14B8A6" if is_approved else "#EF4444"
    icon = "✅" if is_approved else "⚠️"
    text = "Approved — Auto" if is_approved else "Pending Human Review"
    return (
        f'<div style="display:inline-block;padding:6px 14px;border-radius:6px;'
        f'background:{color}1A;border:1px solid {color};color:{color};'
        f'font-family:Inter,sans-serif;font-weight:600;font-size:14px;">'
        f'{icon} {text}</div>'
    )


def _run_pipeline(supplier, country, url, local_file, pdf_url, secondary_url,
                   demo_mode, validate, api_key_input, progress):
    """Shared execution path for both the Quick Test and Advanced tabs.
    Returns (markdown_result, raw_record, banner_html)."""
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input.strip()

    if not demo_mode and not os.environ.get("OPENAI_API_KEY"):
        return ("## ⚠️ No OpenAI API key found\n\nEnter your key above, or enable "
                "**Demo Mode** to try the UI with the lower-quality regex fallback "
                "extractor (no real LLM call, no API key needed)."), {}, ""

    seen = {}

    def cb(step_label, message):
        frac = STEP_PROGRESS.get(step_label, seen.get("last", 0.5))
        seen["last"] = frac
        progress(frac, desc=str(message)[:90])

    progress(0.0, desc="Starting…")
    try:
        record = termsiq_mvp.run_extraction(
            supplier=supplier,
            country=country,
            url=url if not local_file else None,
            local_file=local_file or None,
            pdf_url=pdf_url or None,
            secondary_urls=[secondary_url] if secondary_url else None,
            validate=validate,
            demo=demo_mode,
            progress_callback=cb,
        )
    except Exception as e:
        return (f"## ❌ Extraction failed\n\n```\n{type(e).__name__}: {e}\n```\n\n"
                f"Check the URL or file and try again."), {}, ""

    progress(1.0, desc="Done")
    return format_record_as_markdown(record), record, format_status_banner(record)


def run_preset(preset_name, goldcar_pdf, demo_mode, validate, api_key_input,
                progress=gr.Progress()):
    preset = PRESETS[preset_name]
    pdf_url = goldcar_pdf if preset.get("needs_local_pdf") and goldcar_pdf else None
    return _run_pipeline(
        supplier=preset["supplier"], country=preset["country"], url=preset["url"],
        local_file=None, pdf_url=pdf_url, secondary_url=None,
        demo_mode=demo_mode, validate=validate, api_key_input=api_key_input,
        progress=progress,
    )


def run_advanced(supplier, country, source_mode, url_input, pdf_fallback,
                  file_input, secondary_url, demo_mode, validate, api_key_input,
                  progress=gr.Progress()):
    if not supplier or not country:
        return "## ⚠️ Supplier and country are required.", {}, ""
    if source_mode == "URL" and not url_input:
        return "## ⚠️ Enter a URL, or switch to Upload File.", {}, ""
    if source_mode == "Upload File" and not file_input:
        return "## ⚠️ Upload a file, or switch to URL.", {}, ""

    return _run_pipeline(
        supplier=supplier.strip(), country=country.strip().upper(),
        url=url_input.strip() if source_mode == "URL" else None,
        local_file=file_input if source_mode == "Upload File" else None,
        pdf_url=pdf_fallback.strip() if pdf_fallback else None,
        secondary_url=secondary_url.strip() if secondary_url else None,
        demo_mode=demo_mode, validate=validate, api_key_input=api_key_input,
        progress=progress,
    )


def toggle_goldcar_upload(preset_name):
    needs_it = PRESETS[preset_name].get("needs_local_pdf", False)
    return gr.update(visible=needs_it)


def toggle_source_inputs(source_mode):
    return (gr.update(visible=source_mode == "URL"),
            gr.update(visible=source_mode == "URL"),
            gr.update(visible=source_mode == "Upload File"))


with gr.Blocks(title="TermsIQ — T&C Extraction", theme=theme, css=CUSTOM_CSS) as demo:
    gr.Markdown(
        "# TermsIQ\n"
        "Extract 5 key terms & conditions fields — TPL coverage, grace period, "
        "licence rules, payment rules, cross-border conditions — from car rental "
        "supplier documents."
    )

    with gr.Accordion("OpenAI API Key", open=not bool(os.environ.get("OPENAI_API_KEY"))):
        key_status = "✅ A key is already set in your terminal's environment — the box below will use that automatically if left blank. Only fill it in to use a different key for this run." \
            if os.environ.get("OPENAI_API_KEY") else \
            "⚠️ No key found in your environment — enter one below, or check **Demo Mode** further down to try the UI without one (lower-quality regex extraction instead of a real OpenAI call)."
        gr.Markdown(key_status)
        api_key_box = gr.Textbox(label="OpenAI API Key (optional)", type="password",
                                  placeholder="sk-...", show_label=True)

    with gr.Tabs():
        # ── Quick Test ────────────────────────────────────────────────────
        with gr.Tab("Quick Test"):
            gr.Markdown(
                "Five supplier/country combinations with manually verified ground "
                "truth — results below include a live accuracy check against it."
            )
            preset_dd = gr.Dropdown(choices=list(PRESETS.keys()),
                                     value="Hertz — Spain (ES)", label="Test Case")
            goldcar_pdf_box = gr.Textbox(
                label="Goldcar's page is JS-rendered — provide a local PDF path as fallback",
                placeholder="/path/to/goldcar_terms.pdf", visible=False,
            )
            preset_dd.change(toggle_goldcar_upload, inputs=preset_dd, outputs=goldcar_pdf_box)

            with gr.Row():
                demo_mode_q = gr.Checkbox(label="Demo Mode (no API key, regex fallback)", value=False)
                validate_q = gr.Checkbox(label="Show accuracy vs. ground truth", value=True)
            run_btn_q = gr.Button("Run Extraction", variant="primary")

        # ── Advanced ──────────────────────────────────────────────────────
        with gr.Tab("Advanced"):
            gr.Markdown(
                "Any supplier, any document — no ground truth to compare against, "
                "since this isn't one of the 5 annotated test cases."
            )
            with gr.Row():
                supplier_box = gr.Textbox(label="Supplier name", placeholder="e.g. Europcar")
                country_box = gr.Textbox(label="Pickup country (ISO code)", placeholder="e.g. FR")

            source_mode = gr.Radio(["URL", "Upload File"], value="URL", label="Document source")
            url_box = gr.Textbox(label="Document URL", placeholder="https://...", visible=True)
            pdf_fallback_box = gr.Textbox(
                label="PDF fallback URL or local path (used automatically if the page above is JS-rendered)",
                placeholder="https://... or /path/to/file.pdf", visible=True,
            )
            file_box = gr.File(label="Upload PDF", type="filepath", visible=False)
            secondary_box = gr.Textbox(
                label="Additional source URL (optional — for fields missing from the primary document)",
                placeholder="https://...",
            )
            source_mode.change(toggle_source_inputs, inputs=source_mode,
                                outputs=[url_box, pdf_fallback_box, file_box])

            with gr.Row():
                demo_mode_a = gr.Checkbox(label="Demo Mode (no API key, regex fallback)", value=False)
                validate_a = gr.Checkbox(label="Compare against ground truth (only matches the 5 known combos)",
                                          value=False)
            run_btn_a = gr.Button("Run Extraction", variant="primary")

    gr.Markdown("---\n## Result")
    result_banner = gr.HTML()
    result_md = gr.Markdown()
    with gr.Accordion("Raw JSON", open=False):
        result_json = gr.JSON()

    run_btn_q.click(
        run_preset,
        inputs=[preset_dd, goldcar_pdf_box, demo_mode_q, validate_q, api_key_box],
        outputs=[result_md, result_json, result_banner],
    )
    run_btn_a.click(
        run_advanced,
        inputs=[supplier_box, country_box, source_mode, url_box, pdf_fallback_box,
                file_box, secondary_box, demo_mode_a, validate_a, api_key_box],
        outputs=[result_md, result_json, result_banner],
    )


if __name__ == "__main__":
    demo.queue().launch()
