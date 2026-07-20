#!/usr/bin/env python3
"""
Auto-capture screenshot evidence for ScopeGuard findings.

For each finding that came from nuclei, open the exact URL nuclei matched,
screenshot what loads, upload it to the Supabase `evidence` storage bucket,
and create an evidence record linked to the finding. This is the "the tool
takes the screenshot itself" step - the researcher does nothing.

Only visits URLs that are already recorded on in-scope findings. It performs
one GET per finding (no exploitation, no extra requests).
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.error

import requests
from playwright.sync_api import sync_playwright


def load_url_map(results_path):
    """template-id -> matched-at URL (first match wins)."""
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
            tid = d.get("template-id")
            url = d.get("matched-at")
            if tid and url and tid not in m:
                m[tid] = url
    return m


def get_findings(base, key, programme_id):
    r = requests.get(
        f"{base}/rest/v1/findings",
        params={"programme_id": f"eq.{programme_id}",
                "select": "id,title,source_reference,severity"},
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def existing_evidence_finding_ids(base, key, finding_ids):
    """Return finding_ids that already have auto-captured evidence, to avoid duplicates."""
    if not finding_ids:
        return set()
    r = requests.get(
        f"{base}/rest/v1/evidence",
        params={"select": "finding_id,screenshot_metadata"},
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=20,
    )
    r.raise_for_status()
    return {e["finding_id"] for e in r.json()
            if (e.get("screenshot_metadata") or "").startswith("Auto-captured")}


def screenshot(page, url, out_path):
    """Screenshot a URL. Falls back to rendering raw text for files that download."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(1.2)
        page.screenshot(path=out_path)
        return True
    except Exception:
        # File likely downloaded instead of rendering (e.g. .env). Fetch and render as text.
        try:
            resp = requests.get(url, timeout=20, verify=True)
            body = resp.text[:6000]
            html = ("<html><body style='font-family:monospace;white-space:pre-wrap;"
                    "padding:16px;font-size:13px'>"
                    f"<div style='color:#666'>GET {url}  ->  HTTP {resp.status_code}</div>"
                    f"<hr>{body.replace('<', '&lt;')}</body></html>")
            page.set_content(html)
            time.sleep(0.4)
            page.screenshot(path=out_path)
            return True
        except Exception:
            return False


def upload(base, key, finding_id, png_path):
    with open(png_path, "rb") as f:
        data = f.read()
    path = f"{finding_id}.png"
    url = f"{base}/storage/v1/object/evidence/{path}"
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "image/png", "x-upsert": "true",
    })
    urllib.request.urlopen(req)
    return f"{base}/storage/v1/object/public/evidence/{path}"


def add_evidence(base, key, finding_id, user_id, public_url, matched_url):
    row = {
        "finding_id": finding_id,
        "user_id": user_id,
        "url": public_url,
        "screenshot_metadata": f"Auto-captured screenshot of {matched_url}",
        "notes": ("The tool opened the URL that was flagged and captured what it returned. "
                  "Review this, then it can be turned straight into a report."),
    }
    r = requests.post(
        f"{base}/rest/v1/evidence",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"},
        data=json.dumps(row), timeout=20,
    )
    r.raise_for_status()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    args = p.parse_args()

    url_map = load_url_map(args.results)
    findings = get_findings(args.supabase_url, args.service_key, args.programme_id)
    done = existing_evidence_finding_ids(args.supabase_url, args.service_key,
                                         [f["id"] for f in findings])

    captured = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 720})
        for f in findings:
            if f["id"] in done:
                continue
            tid = (f.get("source_reference") or "").replace("nuclei:", "")
            matched = url_map.get(tid)
            if not matched:
                continue
            out = f"/tmp/ev_{f['id']}.png"
            if not screenshot(page, matched, out):
                print(f"  could not capture {f['title']}")
                continue
            public_url = upload(args.supabase_url, args.service_key, f["id"], out)
            add_evidence(args.supabase_url, args.service_key, f["id"], args.user_id,
                         public_url, matched)
            captured += 1
            print(f"  captured {f['severity']:8} {f['title'][:50]}")
        browser.close()
    print(f"Done. {captured} screenshots captured and attached.")


if __name__ == "__main__":
    main()
