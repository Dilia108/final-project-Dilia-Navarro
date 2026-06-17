# TermsIQ — MVP

**Intelligent Terms & Conditions extraction for car rental distribution.**

TermsIQ reads a supplier's Terms & Conditions document (PDF or web page) and pulls out the five fields that cause the most friction at the rental counter — third-party liability amount, pickup grace period, licence rules, payment rules, and cross-border conditions — returning a structured, API-ready JSON record with a confidence score and source quote for every field.

The MVP extends the POC's single-document pipeline into a multi-source resolution system: when a field is genuinely absent from the main document, it automatically tries documented secondary sources (FAQ pages, country supplements) from `annotation_base.json`, falls back to a supplier-curated value where the Content team has verified one directly with the supplier, and only returns an explicit "needs supplier confirmation" message when no source exists at all — never a silent gap, never a guess.

Five supplier/country combinations are covered out of the box: Hertz ES, Hertz DE, Sixt ES, Sixt DE, and Goldcar ES. The Advanced mode (CLI flags or the Gradio UI's Advanced tab) also accepts any other supplier, country, or document URL.

For the full architecture, the multi-source resolution loop, prompt design, and test results, see **[`mvp_documentation.md`](./mvp_documentation.md)**. This README only covers getting it running.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `openai` and `pypdf` (core pipeline), `gradio` (UI), and `langsmith` (optional tracing — see below).

### 2. Set your OpenAI API key

**macOS / Linux:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:PYTHONIOENCODING = "utf-8"
```

No key? Pass `--demo` (CLI) or check the "Demo Mode" box (Gradio) to run the full pipeline against a local sample file with a regex fallback instead of the LLM — useful for verifying the install works before spending API credits.

### 3. (Optional) Enable LangSmith tracing

```bash
export LANGCHAIN_API_KEY="ls__your_key_here"
```

If set, every extraction call is traced with a confidence-based feedback score. The pipeline runs identically with or without this — it's a pure add-on.

Ground truth (`annotation_base.json`) lives at `../poc/Annotations/annotation_base.json` relative to this folder — the script already knows to look there, so as long as you clone the repo with its folder structure intact, validation and auto-sourced fallbacks work with no extra setup.

---

## Running the CLI

```bash
python termsiq_mvp.py --supplier Hertz --country ES \
    --url "https://images.hertz.com/pdfs/RT_FULL_ES_EN.pdf" \
    --validate
```

Common flags:

| Flag | Purpose |
|---|---|
| `--supplier`, `--country` | Which supplier/country to extract for |
| `--url` | The primary document URL (HTML page or PDF) |
| `--pdf-url` | Fallback PDF URL, used automatically if the primary page is JS-rendered and yields too little text |
| `--local-file` | Path to a local PDF instead of fetching from a URL |
| `--validate` | Embed a ground-truth comparison block in the output (only meaningful for the 5 known supplier/country combos) |
| `--secondary-url` | Add an extra source manually (repeatable). If omitted, secondary sources are auto-loaded from `annotation_base.json` |
| `--no-auto-sources` | Disable that auto-loading — primary document only |
| `--demo` | Run with no API key, against a local sample file |
| `--debug-text` | Print the exact preprocessed text sent to the LLM, for debugging |
| `--output` | Output JSON file path (default: `termsiq_output.json`) |

Run `python termsiq_mvp.py --help` for the complete list.

**Quick demo run with no API key:**
```bash
python termsiq_mvp.py --demo --local-file ../poc/sample_tc.txt --supplier Hertz --country ES --validate
```

---

## Running the Gradio UI

```bash
python gradio_app.py
```

This starts a local web server (Gradio's default, usually `http://127.0.0.1:7860`) and opens two tabs:

- **Quick Test** — five ready-made presets matching the five supplier/country combos above. Pick one, hit Run, and (for Goldcar, whose live page is JS-rendered) optionally provide a local PDF fallback.
- **Advanced** — free-form: any supplier, country, document URL or file upload, plus optional secondary sources. Validation is off by default here since there's no ground truth for arbitrary inputs.

Each result shows a status banner, a field-by-field breakdown with confidence badges and source quotes, and the raw JSON in a collapsible section. If `OPENAI_API_KEY` is already set in your environment, the UI detects it automatically — the password field is only for overriding it for a single run.

---

## File structure

```
mvp/
├── termsiq_mvp.py        ← core pipeline (CLI entry point + run_extraction())
├── gradio_app.py          ← Gradio UI, built on top of run_extraction()
├── requirements.txt
├── mvp_documentation.md   ← full technical writeup: architecture, resolution
│                             logic, prompt design, live test results
├── mvp_terminal_output.md ← captured terminal output from CLI test runs
├── termsiq_output.json    ← sample output from a live run
├── screenshots/           ← LangSmith tracing dashboard screenshots
└── README.md              ← this file
```

`annotation_base.json` (ground truth, owned by the Content team) lives one level up, in `poc/Annotations/` — shared between the POC and MVP pipelines rather than duplicated.
