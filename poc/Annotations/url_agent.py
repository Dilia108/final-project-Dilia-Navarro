#!/usr/bin/env python3
"""
TermsIQ URL Validity Agent
Checks all URLs in annotation_base.json and updates their url_status field.
Run periodically (daily via n8n or Task Scheduler) to detect 404s, JS-rendered
pages, and redirects before they cause extraction failures.

Usage:
    python url_agent.py                              # check all URLs
    python url_agent.py --record SIXT_ES             # check one record only
    python url_agent.py --dry-run                    # report without writing
    python url_agent.py --secondary-only             # skip primary PDFs
    python url_agent.py --annotation annotation_base.json
    python url_agent.py --notify --smtp-to you@email.com

Email config (set via env vars or CLI args):
    TERMSIQ_SMTP_HOST     SMTP server host (e.g. smtp.gmail.com)
    TERMSIQ_SMTP_PORT     SMTP port (default 587)
    TERMSIQ_SMTP_USER     SMTP username / sender address
    TERMSIQ_SMTP_PASS     SMTP password / app password
    TERMSIQ_NOTIFY_TO     Recipient email address
"""

import json
import argparse
import urllib.request
import urllib.error
import urllib.parse
import time
import sys
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
DEFAULT_ANNOTATION_FILE = "annotation_base.json"
DEFAULT_LOG_FILE        = "url_agent_log.json"
JS_RENDER_THRESHOLD     = 5000    # chars — below this from a web page = likely JS shell
REQUEST_TIMEOUT         = 15      # seconds per URL
DELAY_BETWEEN_REQUESTS  = 1.5     # seconds — be polite to servers
USER_AGENT              = "TermsIQ-URLAgent/1.0 (monitoring@termsiq.io)"

# Status values (must match annotation_base.json schema)
STATUS_OK           = "OK"
STATUS_404          = "404"
STATUS_BLOCKED      = "BLOCKED"    # 403 — server blocked bot; URL likely still valid
STATUS_JS_RENDERED  = "JS_RENDERED"
STATUS_REDIRECT     = "REDIRECT"
STATUS_TIMEOUT      = "TIMEOUT"
STATUS_ERROR        = "ERROR"
STATUS_SKIP         = "SKIP"       # local files, session-authenticated, etc.

# Statuses that require human action
ACTION_STATUSES = {STATUS_404, STATUS_JS_RENDERED, STATUS_REDIRECT,
                   STATUS_TIMEOUT, STATUS_ERROR}

SKIP_PREFIXES = ["local://", "session://", "file://"]


# ── URL Checking ─────────────────────────────────────────────────────────────

def check_url(url: str) -> dict:
    """Check a single URL and return a status dict."""
    if any(url.startswith(p) for p in SKIP_PREFIXES):
        return {"status": STATUS_SKIP, "note": "Local or session-authenticated — cannot check remotely"}

    req    = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    result = {"status": STATUS_ERROR, "http_code": None, "content_length": None,
              "redirect_url": None, "note": ""}

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            final_url    = resp.url
            http_code    = resp.status
            content_type = resp.headers.get("Content-Type", "")
            content      = resp.read()
            content_len  = len(content)

            result["http_code"]      = http_code
            result["content_length"] = content_len

            # Detect redirect
            parsed_orig  = urllib.parse.urlparse(url)
            parsed_final = urllib.parse.urlparse(final_url)
            if parsed_orig.netloc != parsed_final.netloc or \
               parsed_orig.path   != parsed_final.path:
                result["status"]       = STATUS_REDIRECT
                result["redirect_url"] = final_url
                result["note"]         = f"Redirected to: {final_url}"
                return result

            # Detect JS-rendered page
            if "text/html" in content_type.lower():
                text_clean = re.sub(r"\s+", " ",
                             re.sub(r"<[^>]+>", " ",
                             content.decode("utf-8", errors="ignore"))).strip()
                if len(text_clean) < JS_RENDER_THRESHOLD:
                    result["status"] = STATUS_JS_RENDERED
                    result["note"]   = (f"Only {len(text_clean):,} chars of text extracted "
                                        f"— likely JS-rendered. Use PDF fallback.")
                    return result

            result["status"] = STATUS_OK
            result["note"]   = f"{content_len:,} bytes | {content_type.split(';')[0].strip()}"
            return result

    except urllib.error.HTTPError as e:
        result["http_code"] = e.code
        if e.code == 404:
            result["status"] = STATUS_404
            result["note"]   = "HTTP 404: Not Found — URL no longer exists"
        elif e.code == 403:
            result["status"] = STATUS_BLOCKED
            result["note"]   = "HTTP 403: Server blocks automated access. URL likely valid — verify manually."
        else:
            result["status"] = STATUS_ERROR
            result["note"]   = f"HTTP {e.code}: {e.reason}"
        return result

    except urllib.error.URLError as e:
        reason = str(e.reason)
        result["status"] = STATUS_TIMEOUT if "timed out" in reason.lower() else STATUS_ERROR
        result["note"]   = (f"Timed out after {REQUEST_TIMEOUT}s" if "timed out" in reason.lower()
                            else f"URL error: {reason}")
        return result

    except Exception as e:
        result["status"] = STATUS_ERROR
        result["note"]   = f"Unexpected error: {e}"
        return result


# ── Record Helpers ────────────────────────────────────────────────────────────

def collect_urls(record: dict) -> list[dict]:
    """Extract all URLs from a record with metadata."""
    urls    = []
    sources = record.get("sources", {})

    if "primary" in sources:
        src = sources["primary"]
        urls.append({"path": "sources.primary", "url": src["url"],
                     "current_status": src.get("url_status", "UNCHECKED")})

    if "primary_pdf_fallback" in sources:
        src = sources["primary_pdf_fallback"]
        urls.append({"path": "sources.primary_pdf_fallback", "url": src["url"],
                     "current_status": src.get("url_status", "UNCHECKED")})

    for i, src in enumerate(sources.get("secondary", [])):
        urls.append({"path": f"sources.secondary[{i}]", "url": src["url"],
                     "current_status": src.get("url_status", "UNCHECKED"),
                     "fields_covered": src.get("fields_covered", [])})
    return urls


def update_status_in_record(record: dict, path: str, result: dict) -> None:
    """Write url_status (and redirect_url if applicable) back into the record."""
    sources = record["sources"]
    if path == "sources.primary":
        sources["primary"]["url_status"] = result["status"]
        if result.get("redirect_url"):
            sources["primary"]["redirect_url"] = result["redirect_url"]
    elif path == "sources.primary_pdf_fallback":
        sources["primary_pdf_fallback"]["url_status"] = result["status"]
    elif path.startswith("sources.secondary["):
        idx = int(path.split("[")[1].rstrip("]"))
        sources["secondary"][idx]["url_status"] = result["status"]
        if result.get("redirect_url"):
            sources["secondary"][idx]["redirect_url"] = result["redirect_url"]


def status_icon(status: str) -> str:
    return {"OK": "✓", "404": "✗", "BLOCKED": "⊘", "JS_RENDERED": "⚠",
            "REDIRECT": "→", "TIMEOUT": "⏱", "ERROR": "✗", "SKIP": "–"}.get(status, "?")


# ── Log File ──────────────────────────────────────────────────────────────────

def write_log(log_path: str, run_record: dict) -> None:
    """
    Append a run record to the JSON log file.
    Log file is a JSON array — one entry per agent run.
    Keeps the last 90 runs (approx 3 months of daily runs).
    """
    MAX_LOG_ENTRIES = 90
    log_file = Path(log_path)

    if log_file.exists():
        try:
            with open(log_file, encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []
    else:
        log = []

    log.append(run_record)
    log = log[-MAX_LOG_ENTRIES:]   # keep only the most recent runs

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ── Email Notification ────────────────────────────────────────────────────────

def send_notification(issues: list[dict], run_timestamp: str,
                      smtp_host: str, smtp_port: int,
                      smtp_user: str, smtp_pass: str,
                      notify_to: str) -> bool:
    """
    Send an email notification listing all action-required issues.
    Returns True if sent successfully.
    """
    subject = f"⚠ TermsIQ URL Agent — {len(issues)} issue(s) detected — {run_timestamp[:10]}"

    # Plain text body
    lines = [
        "TermsIQ URL Validity Agent — Action Required",
        "=" * 52,
        f"Run timestamp : {run_timestamp}",
        f"Issues found  : {len(issues)}",
        "",
        "The following URLs require attention:",
        "",
    ]
    for i, issue in enumerate(issues, 1):
        lines += [
            f"{i}. [{issue['record']}] {issue['path']}",
            f"   Status : {issue['status']}",
            f"   URL    : {issue['url']}",
            f"   Note   : {issue['note']}",
            "",
        ]
    lines += [
        "Action required:",
        "  404       → URL deleted. Find replacement and update annotation_base.json.",
        "  JS_RENDERED → Page now JS-rendered. Add or update PDF fallback URL.",
        "  REDIRECT  → URL moved. Update annotation_base.json with new URL.",
        "  TIMEOUT   → Server slow. Retry manually before taking action.",
        "  ERROR     → Unexpected error. Check manually.",
        "",
        "Update annotation_base.json and re-run: python url_agent.py",
        "",
        "— TermsIQ URL Agent",
    ]
    body_text = "\n".join(lines)

    # HTML body
    html_rows = ""
    status_colors = {
        "404": "#dc2626", "JS_RENDERED": "#d97706", "REDIRECT": "#2563eb",
        "TIMEOUT": "#7c3aed", "ERROR": "#dc2626",
    }
    for issue in issues:
        color = status_colors.get(issue["status"], "#374151")
        html_rows += f"""
        <tr>
          <td style="padding:8px;border:1px solid #e5e7eb;font-weight:bold">{issue['record']}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;font-size:12px;color:#6b7280">{issue['path']}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;color:{color};font-weight:bold">{issue['status']}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;font-size:12px">{issue['note'][:100]}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;font-size:11px;color:#6b7280;word-break:break-all">{issue['url']}</td>
        </tr>"""

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#111827;max-width:900px">
    <h2 style="color:#dc2626">⚠ TermsIQ URL Agent — Action Required</h2>
    <p><strong>{len(issues)} issue(s) detected</strong> during scheduled URL check on {run_timestamp[:10]}.</p>
    <table style="border-collapse:collapse;width:100%;font-size:13px">
      <thead><tr style="background:#f3f4f6">
        <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Record</th>
        <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Source</th>
        <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Status</th>
        <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Note</th>
        <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">URL</th>
      </tr></thead>
      <tbody>{html_rows}</tbody>
    </table>
    <h3>What to do</h3>
    <ul>
      <li><strong>404</strong> — URL deleted. Find replacement and update <code>annotation_base.json</code>.</li>
      <li><strong>JS_RENDERED</strong> — Page is now JS-rendered. Add or update PDF fallback URL.</li>
      <li><strong>REDIRECT</strong> — URL moved. Update <code>annotation_base.json</code> with the new URL.</li>
      <li><strong>TIMEOUT</strong> — Server slow. Retry manually before taking action.</li>
      <li><strong>ERROR</strong> — Unexpected error. Check URL manually.</li>
    </ul>
    <p style="color:#6b7280;font-size:12px">— TermsIQ URL Agent | {run_timestamp}</p>
    </body></html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = smtp_user
        msg["To"]      = notify_to
        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, notify_to, msg.as_string())
        return True

    except Exception as e:
        print(f"  ⚠ Email notification failed: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TermsIQ URL Validity Agent")
    parser.add_argument("--annotation",     default=DEFAULT_ANNOTATION_FILE)
    parser.add_argument("--log",            default=DEFAULT_LOG_FILE,
                        help=f"JSON log file path (default: {DEFAULT_LOG_FILE})")
    parser.add_argument("--record",         default=None,
                        help="Check only this record ID (e.g. SIXT_ES)")
    parser.add_argument("--dry-run",        action="store_true",
                        help="Report without writing to JSON or sending email")
    parser.add_argument("--secondary-only", action="store_true",
                        help="Check secondary URLs only (skip primary PDFs)")
    parser.add_argument("--unchecked-only", action="store_true",
                        help="Only check URLs currently marked UNCHECKED")
    # Email args (fall back to env vars)
    parser.add_argument("--notify",         action="store_true",
                        help="Send email notification when issues are found")
    parser.add_argument("--smtp-host",      default=os.getenv("TERMSIQ_SMTP_HOST", "smtp.gmail.com"))
    parser.add_argument("--smtp-port",      type=int,
                        default=int(os.getenv("TERMSIQ_SMTP_PORT", "587")))
    parser.add_argument("--smtp-user",      default=os.getenv("TERMSIQ_SMTP_USER", ""))
    parser.add_argument("--smtp-pass",      default=os.getenv("TERMSIQ_SMTP_PASS", ""))
    parser.add_argument("--smtp-to",        default=os.getenv("TERMSIQ_NOTIFY_TO", ""))
    args = parser.parse_args()

    # Load annotation base
    try:
        with open(args.annotation, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.annotation} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON — {e}")
        sys.exit(1)

    records = data["records"]
    if args.record:
        records = [r for r in records if r["id"] == args.record]
        if not records:
            print(f"Error: Record '{args.record}' not found.")
            sys.exit(1)

    run_timestamp = datetime.now(timezone.utc).isoformat()
    total_checked = 0
    total_ok      = 0
    total_blocked = 0
    total_skipped = 0
    issues        = []          # action-required issues only
    all_results   = []          # full log of every URL checked

    print("=" * 64)
    print("  TermsIQ URL Validity Agent")
    print(f"  {run_timestamp}")
    print("=" * 64)

    for record in records:
        print(f"\n  [{record['id']}] {record['supplier']} / {record['country']}")
        urls = collect_urls(record)

        for url_info in urls:
            url     = url_info["url"]
            path    = url_info["path"]
            current = url_info.get("current_status", "UNCHECKED")

            if args.secondary_only and "secondary" not in path:
                continue
            if args.unchecked_only and current not in ("UNCHECKED", None):
                print(f"    – {path}: {current} (skipped — already checked)")
                total_skipped += 1
                continue

            print(f"    Checking {path}...", end=" ", flush=True)
            time.sleep(DELAY_BETWEEN_REQUESTS)

            result = check_url(url)
            icon   = status_icon(result["status"])
            print(f"{icon} {result['status']}  {result['note'][:75]}")

            # Tally
            total_checked += 1
            if result["status"] == STATUS_OK:
                total_ok += 1
            elif result["status"] == STATUS_BLOCKED:
                total_blocked += 1
            elif result["status"] == STATUS_SKIP:
                total_skipped += 1

            # Collect action-required issues
            if result["status"] in ACTION_STATUSES:
                issues.append({
                    "record":   record["id"],
                    "supplier": record["supplier"],
                    "country":  record["country"],
                    "path":     path,
                    "url":      url,
                    "status":   result["status"],
                    "note":     result["note"],
                    "fields_covered": url_info.get("fields_covered", []),
                })

            # Full log entry
            all_results.append({
                "record":      record["id"],
                "path":        path,
                "url":         url,
                "status":      result["status"],
                "http_code":   result.get("http_code"),
                "note":        result["note"],
                "redirect_url": result.get("redirect_url"),
            })

            # Write status back to annotation base
            if not args.dry_run:
                update_status_in_record(record, path, result)

    # ── Write annotation base ─────────────────────────────────────────────────
    if not args.dry_run:
        data["url_check"]["last_checked"] = run_timestamp
        with open(args.annotation, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n  ✓ Annotation base updated: {args.annotation}")

    # ── Write log file ────────────────────────────────────────────────────────
    run_record = {
        "run_timestamp":  run_timestamp,
        "annotation":     args.annotation,
        "total_checked":  total_checked,
        "total_ok":       total_ok,
        "total_blocked":  total_blocked,
        "total_skipped":  total_skipped,
        "issues_count":   len(issues),
        "issues":         issues,
        "all_results":    all_results,
    }
    if not args.dry_run:
        write_log(args.log, run_record)
        print(f"  ✓ Run logged to: {args.log}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 64)
    print("  SUMMARY")
    print(f"  Checked  : {total_checked}")
    print(f"  OK       : {total_ok}")
    print(f"  Blocked  : {total_blocked}  (403 — server blocks bots, URL likely valid)")
    print(f"  Skipped  : {total_skipped}  (local/session files or already-checked filter)")
    print(f"  Issues   : {len(issues)}  (action required)")
    print("=" * 64)

    if issues:
        print("\n  ACTION REQUIRED:")
        for issue in issues:
            print(f"\n  [{issue['record']}] {issue['path']}")
            print(f"    Status : {issue['status']}")
            print(f"    URL    : {issue['url']}")
            print(f"    Note   : {issue['note']}")
            if issue.get("fields_covered"):
                print(f"    Fields : {', '.join(issue['fields_covered'])}")
    else:
        print("\n  All checked URLs are healthy. No action required.")

    # ── Email notification ────────────────────────────────────────────────────
    if args.notify and issues and not args.dry_run:
        if not all([args.smtp_host, args.smtp_user, args.smtp_pass, args.smtp_to]):
            print("\n  ⚠ Email notification skipped — SMTP credentials not fully configured.")
            print("    Set --smtp-host, --smtp-user, --smtp-pass, --smtp-to")
            print("    or env vars TERMSIQ_SMTP_HOST / USER / PASS / TERMSIQ_NOTIFY_TO")
        else:
            print(f"\n  Sending notification to {args.smtp_to}...", end=" ", flush=True)
            ok = send_notification(
                issues, run_timestamp,
                args.smtp_host, args.smtp_port,
                args.smtp_user, args.smtp_pass, args.smtp_to
            )
            print("✓ Sent" if ok else "✗ Failed (see above)")
    elif args.notify and not issues:
        print("\n  Email notification skipped — no issues to report.")

    # Exit with non-zero code if issues found (useful for n8n IF node)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
