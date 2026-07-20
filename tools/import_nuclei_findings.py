#!/usr/bin/env python3
"""
Import nuclei JSONL results into ScopeGuard's Supabase `findings` table.

This is the bridge between the scanner and the app: nuclei finds the issues,
this drops them straight into the user's Findings list, already sorted by
severity and written in plain English. Human review, evidence and reporting
still happen inside the app - nothing here contacts a target.

Usage:
  import_nuclei_findings.py --results nuclei-results.jsonl \
      --user-id <uuid> --programme-id <uuid> \
      --supabase-url https://<ref>.supabase.co --service-key <key>
"""
import argparse
import json
import sys
import urllib.request

SEV_MAP = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Informational",
    "informational": "Informational",
    "unknown": "Informational",
}

PLAIN = {
    "Critical": "Critical - look at this first. It usually means something sensitive is exposed or directly exploitable.",
    "High": "High - a serious issue that's well worth reporting once you've confirmed it.",
    "Medium": "Medium - a real weakness, but lower urgency than High or Critical.",
    "Low": "Low - a minor or hardening issue. Often best-practice rather than a strong bug on its own.",
    "Informational": "Info - not a bug by itself, but useful context that can support a bigger finding.",
}


def load_findings(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def to_row(item, user_id, programme_id):
    info = item.get("info", {}) or {}
    sev = SEV_MAP.get(str(info.get("severity", "")).lower(), "Informational")
    name = info.get("name") or item.get("template-id") or "Unnamed finding"
    matched = item.get("matched-at") or item.get("host") or ""
    desc = (info.get("description") or "").strip()
    refs = info.get("reference") or []
    if isinstance(refs, str):
        refs = [refs]

    body = []
    if desc:
        body.append(desc)
    body.append(f"What this means: {PLAIN[sev]}")
    if matched:
        body.append(f"Where nuclei saw it: {matched}")
    body.append("Next step: confirm it yourself, capture a screenshot as evidence, "
                "then turn it into a report. Only do this on assets that are in scope "
                "and where the programme allows automated scanning.")

    notes_parts = [f"Detected by nuclei template: {item.get('template-id', 'unknown')}"]
    if refs:
        notes_parts.append("References:\n" + "\n".join(f"- {r}" for r in refs[:5]))

    return {
        "user_id": user_id,
        "programme_id": programme_id,
        "asset_id": None,
        "title": name[:240],
        "description": "\n\n".join(body),
        "severity": sev,
        "status": "New",
        "source_reference": f"nuclei:{item.get('template-id', 'unknown')}",
        "notes": "\n\n".join(notes_parts),
    }


def post_rows(rows, supabase_url, service_key):
    url = f"{supabase_url}/rest/v1/findings"
    data = json.dumps(rows).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    with urllib.request.urlopen(req) as r:
        return r.status


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    args = p.parse_args()

    findings = load_findings(args.results)
    if not findings:
        print("No nuclei findings to import.")
        return

    # de-duplicate on template-id + matched host within this batch
    seen = set()
    rows = []
    for it in findings:
        key = (it.get("template-id"), it.get("matched-at"))
        if key in seen:
            continue
        seen.add(key)
        rows.append(to_row(it, args.user_id, args.programme_id))

    status = post_rows(rows, args.supabase_url, args.service_key)
    print(f"Imported {len(rows)} findings (HTTP {status}).")
    bysev = {}
    for r in rows:
        bysev[r["severity"]] = bysev.get(r["severity"], 0) + 1
    print("By severity:", bysev)


if __name__ == "__main__":
    main()
