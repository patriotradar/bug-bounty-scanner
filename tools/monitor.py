#!/usr/bin/env python3
"""
ScopeGuard monitoring - re-check a programme's targets and flag only what's NEW.

Given a fresh nuclei scan, this compares against what is already recorded for the
programme and imports ONLY findings that were not there last time - each captured,
screenshotted and marked as newly detected - so the researcher is early to a change
without being spammed with the same findings every run. It also reports anything
that has disappeared since the last check (a fix, or a moved endpoint).

Scope-safe: only ever works with results from targets the caller chose to scan,
which should be programmes whose rules allow automated scanning. One GET per new
finding for the screenshot; no exploitation.
"""
import argparse
import json
import time
import urllib.request

import requests
from playwright.sync_api import sync_playwright

SEV_MAP = {"critical": "Critical", "high": "High", "medium": "Medium",
           "low": "Low", "info": "Informational", "informational": "Informational",
           "unknown": "Informational"}
PLAIN = {
    "Critical": "Critical - look at this first. Something sensitive is likely exposed or directly exploitable.",
    "High": "High - a serious issue that's well worth reporting once confirmed.",
    "Medium": "Medium - a real weakness, lower urgency than High or Critical.",
    "Low": "Low - minor or hardening issue, often best-practice.",
    "Informational": "Info - not a bug on its own, but useful supporting context.",
}


def sig(item):
    """Stable signature for a finding: template + where it was seen."""
    return f"{item.get('template-id','')}|{item.get('matched-at','')}"


def load_results(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    # de-dup within this scan by signature
    seen, uniq = set(), []
    for it in out:
        s = sig(it)
        if s not in seen:
            seen.add(s)
            uniq.append(it)
    return uniq


def tmpl_key(item):
    """Compare findings on the nuclei template id - the issue type - within a programme."""
    return item.get("template-id", "")


def existing_template_ids(base, key, programme_id):
    r = requests.get(f"{base}/rest/v1/findings",
                     params={"programme_id": f"eq.{programme_id}",
                             "select": "id,source_reference"},
                     headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    # source_reference is "nuclei:<template-id>" or "nuclei:<template-id>|<matched-at>"
    out = set()
    for row in r.json():
        ref = row.get("source_reference") or ""
        if ref.startswith("nuclei:"):
            out.add(ref.replace("nuclei:", "").split("|")[0])
    return out


def screenshot(page, url, out_path):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(1.2)
        page.screenshot(path=out_path)
        return True
    except Exception:
        try:
            resp = requests.get(url, timeout=20)
            html = ("<html><body style='font-family:monospace;white-space:pre-wrap;"
                    f"padding:16px;font-size:13px'><div style='color:#666'>GET {url} -> "
                    f"HTTP {resp.status_code}</div><hr>{resp.text[:6000].replace('<','&lt;')}"
                    "</body></html>")
            page.set_content(html)
            time.sleep(0.4)
            page.screenshot(path=out_path)
            return True
        except Exception:
            return False


def add_finding(base, key, user_id, programme_id, item, first_seen):
    info = item.get("info", {}) or {}
    sev = SEV_MAP.get(str(info.get("severity", "")).lower(), "Informational")
    matched = item.get("matched-at") or ""
    desc = (info.get("description") or "").strip()
    body = [p for p in [desc, f"What this means: {PLAIN[sev]}",
                        f"Where nuclei saw it: {matched}" if matched else "",
                        "Next step: confirm it, keep the captured screenshot, turn it into a report."] if p]
    row = {
        "user_id": user_id, "programme_id": programme_id, "asset_id": None,
        "title": (info.get("name") or item.get("template-id") or "Finding")[:240],
        "description": "\n\n".join(body), "severity": sev, "status": "New",
        "source_reference": f"nuclei:{sig(item)}",
        "notes": f"NEWLY DETECTED by monitoring on {first_seen}. Detected by nuclei template: {item.get('template-id','unknown')}",
    }
    r = requests.post(f"{base}/rest/v1/findings",
                      headers={"apikey": key, "Authorization": f"Bearer {key}",
                               "Content-Type": "application/json", "Prefer": "return=representation"},
                      data=json.dumps(row), timeout=20)
    r.raise_for_status()
    return r.json()[0]["id"]


def attach_screenshot(base, key, page, finding_id, user_id, matched):
    out = f"/tmp/mon_{finding_id}.png"
    if not matched or not screenshot(page, matched, out):
        return
    with open(out, "rb") as fh:
        data = fh.read()
    urllib.request.urlopen(urllib.request.Request(
        f"{base}/storage/v1/object/evidence/{finding_id}.png", data=data, method="POST",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "image/png", "x-upsert": "true"}))
    public = f"{base}/storage/v1/object/public/evidence/{finding_id}.png"
    requests.post(f"{base}/rest/v1/evidence",
                  headers={"apikey": key, "Authorization": f"Bearer {key}",
                           "Content-Type": "application/json", "Prefer": "return=minimal"},
                  data=json.dumps({"finding_id": finding_id, "user_id": user_id, "url": public,
                                   "screenshot_metadata": f"Auto-captured screenshot of {matched}",
                                   "notes": "Captured automatically by monitoring when this finding first appeared."}),
                  timeout=20)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    p.add_argument("--now", default=time.strftime("%Y-%m-%d"))
    args = p.parse_args()

    results = load_results(args.results)
    existing = existing_template_ids(args.supabase_url, args.service_key, args.programme_id)
    fresh_keys = {tmpl_key(it) for it in results}

    new_items = [it for it in results if tmpl_key(it) not in existing]
    resolved = existing - fresh_keys

    print(f"Monitoring run {args.now}: scanned {len(results)}, "
          f"already known {len(results) - len(new_items)}, NEW {len(new_items)}, "
          f"disappeared since last check {len(resolved)}.")

    if new_items:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1000, "height": 720})
            for it in new_items:
                fid = add_finding(args.supabase_url, args.service_key, args.user_id,
                                  args.programme_id, it, args.now)
                attach_screenshot(args.supabase_url, args.service_key, page, fid,
                                  args.user_id, it.get("matched-at"))
                sev = (it.get("info", {}) or {}).get("severity", "?")
                print(f"  NEW [{sev}] {(it.get('info',{}) or {}).get('name','')[:55]}")
            browser.close()
    if resolved:
        print(f"  Note: {len(resolved)} finding(s) no longer detected - may have been fixed.")


if __name__ == "__main__":
    main()
