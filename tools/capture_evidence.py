#!/usr/bin/env python3
"""
Collect evidence-driven proof for ScopeGuard findings.

For each finding that came from nuclei, this re-requests the exact URL and
captures everything a triager needs to reproduce it WITHOUT asking for more:
  HTTP request, response status, relevant headers, response body (secrets
  redacted), timestamp, response size, content type, a SHA-256 of the body,
  and a screenshot.

It then ASSESSES that evidence (see assess.py): what sensitive data is really
present, a severity justified by the evidence (not the template), a confidence
level, a descriptive title, and a verification status - and updates the finding
accordingly. Scanner findings are never marked "Researcher verified".

One GET per finding. No exploitation.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assess as A

RELEVANT_HEADERS = ["content-type", "content-length", "server", "x-powered-by", "content-disposition",
                    "cache-control", "www-authenticate", "location", "set-cookie", "last-modified"]

import re as _re
_CTRL = _re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean(s):
    """Strip NUL and other control chars Postgres text columns reject."""
    return _CTRL.sub("", s or "")


def looks_binary(body):
    return "\x00" in (body or "")[:2048]


def get_findings(base, key, programme_id):
    r = requests.get(f"{base}/rest/v1/findings",
                     params={"programme_id": f"eq.{programme_id}",
                             "select": "id,title,source_reference,severity"},
                     headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    return r.json()


def already_done(base, key):
    r = requests.get(f"{base}/rest/v1/evidence",
                     params={"select": "finding_id,screenshot_metadata"},
                     headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    return {e["finding_id"] for e in r.json() if (e.get("screenshot_metadata") or "").startswith("Auto-captured")}


def load_url_map(results_path):
    m = {}
    with open(results_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            tid, url = d.get("template-id"), d.get("matched-at")
            if tid and url and tid not in m:
                m[tid] = url
    return m


def fetch(url, user_agent):
    """GET the URL and capture the full request/response evidence."""
    headers = {"User-Agent": user_agent} if user_agent else {}
    t0 = time.time()
    resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
    elapsed = int((time.time() - t0) * 1000)
    raw = resp.text or ""
    body = (f"[binary content - {len(resp.content)} bytes, not shown as text]"
            if looks_binary(raw) else raw)
    return {
        "req_method": "GET", "req_url": url,
        "req_headers": dict(resp.request.headers),
        "status": resp.status_code,
        "resp_headers": {k: v for k, v in resp.headers.items() if k.lower() in RELEVANT_HEADERS},
        "content_type": resp.headers.get("Content-Type", ""),
        "size": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        "elapsed_ms": elapsed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "body": body,
    }


def screenshot(page, url, out_path):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(1.0)
        page.screenshot(path=out_path)
        return True
    except Exception:
        try:
            resp = requests.get(url, timeout=20)
            html = ("<html><body style='font-family:monospace;white-space:pre-wrap;padding:16px;font-size:13px'>"
                    f"<div style='color:#666'>GET {url} -> HTTP {resp.status_code}</div><hr>"
                    f"{resp.text[:6000].replace('<','&lt;')}</body></html>")
            page.set_content(html)
            time.sleep(0.3)
            page.screenshot(path=out_path)
            return True
        except Exception:
            return False


def upload_png(base, key, finding_id, png):
    with open(png, "rb") as f:
        data = f.read()
    req = urllib.request.Request(f"{base}/storage/v1/object/evidence/{finding_id}.png", data=data, method="POST",
                                 headers={"apikey": key, "Authorization": f"Bearer {key}",
                                          "Content-Type": "image/png", "x-upsert": "true"})
    urllib.request.urlopen(req)
    return f"{base}/storage/v1/object/public/evidence/{finding_id}.png"


def req_block(ev):
    lines = [f"{ev['req_method']} {ev['req_url']}"]
    for k, v in ev["req_headers"].items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def resp_block(ev):
    lines = [f"HTTP {ev['status']}"]
    for k, v in ev["resp_headers"].items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append(f"[response size: {ev['size']} bytes | content-type: {ev['content_type'] or 'unknown'} | "
                 f"sha256: {ev['sha256']} | captured: {ev['timestamp']} | {ev['elapsed_ms']} ms]")
    return "\n".join(lines)


def save_evidence(base, key, finding_id, user_id, public_url, ev, a):
    observed = "\n".join(f"- {o}" for o in a["observed"])
    # Labelled sections so the report builder can lift each one cleanly.
    notes = (f"OBSERVED DATA:\n{observed}\n\n"
             f"SEVERITY JUSTIFICATION:\n{a['severity_justification']}\n\n"
             f"CONFIDENCE:\n{a['confidence']} - {a['confidence_reason']}\n\n"
             f"VERIFICATION STATUS:\n{a['verification_status']}\n\n"
             f"REDACTED RESPONSE BODY:\n{a['redacted_body']}")
    row = {
        "finding_id": finding_id, "user_id": user_id, "url": public_url,
        "request_metadata": clean(req_block(ev)),
        "response_metadata": clean(resp_block(ev)),
        "screenshot_metadata": clean(f"Auto-captured screenshot of {ev['req_url']}"),
        "notes": clean(notes),
    }
    requests.post(f"{base}/rest/v1/evidence",
                  headers={"apikey": key, "Authorization": f"Bearer {key}",
                           "Content-Type": "application/json", "Prefer": "return=minimal"},
                  data=json.dumps(row), timeout=20).raise_for_status()


def update_finding(base, key, finding_id, a):
    observed = ", ".join(a["observed"])
    desc = (f"{a['title']}\n\n"
            f"What was found: {observed}.\n\n"
            f"Severity ({a['severity']}): {a['severity_justification']}\n\n"
            f"Confidence ({a['confidence']}): {a['confidence_reason']}\n\n"
            f"This is a scanner lead - status '{a['verification_status']}'. Confirm it by hand "
            f"before reporting; do not submit unverified.")
    row = {"title": clean(a["title"])[:240], "severity": a["severity"], "description": clean(desc),
           "confidence": a["confidence"], "verification_status": a["verification_status"]}
    requests.patch(f"{base}/rest/v1/findings?id=eq.{finding_id}",
                   headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                   data=json.dumps(row), timeout=20).raise_for_status()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    p.add_argument("--user-agent", default="")
    args = p.parse_args()

    url_map = load_url_map(args.results)
    findings = get_findings(args.supabase_url, args.service_key, args.programme_id)
    done = already_done(args.supabase_url, args.service_key)

    captured = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 720})
        for f in findings:
            if f["id"] in done:
                continue
            tid = (f.get("source_reference") or "").replace("nuclei:", "").split("|")[0]
            matched = url_map.get(tid)
            if not matched:
                continue
            try:
                ev = fetch(matched, args.user_agent)
            except Exception as e:
                print(f"  fetch failed {matched}: {e}")
                continue
            a = A.assess(ev["body"], ev["status"], ev["resp_headers"], matched,
                         template_sev=f.get("severity", ""), fallback_title=f.get("title", ""))
            out = f"/tmp/ev_{f['id']}.png"
            if not screenshot(page, matched, out):
                print(f"  could not screenshot {matched}")
                continue
            public_url = upload_png(args.supabase_url, args.service_key, f["id"], out)
            save_evidence(args.supabase_url, args.service_key, f["id"], args.user_id, public_url, ev, a)
            update_finding(args.supabase_url, args.service_key, f["id"], a)
            captured += 1
            print(f"  {a['severity']:13} conf={a['confidence']:6} {a['title'][:60]}")
        browser.close()
    print(f"Done. {captured} findings assessed with full evidence.")


if __name__ == "__main__":
    main()
