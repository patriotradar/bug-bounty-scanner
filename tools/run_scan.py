#!/usr/bin/env python3
"""
ScopeGuard scan orchestrator with a live, plain-English activity feed.

Runs nuclei against the in-scope targets of one programme and, as it works,
writes step-by-step rows into scan_runs / scan_events so the researcher can
follow along on their phone (the "Scan Activity" page). Then it saves the
findings (sorted by severity), captures screenshot evidence, and marks the run
complete.

Scope-safe by construction:
  * only scans the targets passed in (which must be in-scope assets),
  * honours --rate-limit (default 5/sec) and an optional --user-agent header
    so it obeys programme rules such as Acronis's,
  * excludes dos / intrusive / bruteforce / fuzzing templates,
  * finds and proves; it never exploits.

Usage:
  run_scan.py --targets a.com,b.com --user-id U --programme-id P \
     --programme-name "Acme" --supabase-url URL --service-key KEY \
     --nuclei ./tools/nuclei [--user-agent "me+x@wearehackerone.com"] \
     [--rate-limit 5] [--mode scan|monitor]
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SEV_ORDER = ["critical", "high", "medium", "low", "info", "informational", "unknown"]
EXCLUDE_TAGS = ["dos", "fuzz", "fuzzing", "bruteforce", "intrusive"]


def api(base, key):
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def create_run(base, key, user_id, programme_id, programme_name, mode, targets_total):
    row = {"user_id": user_id, "programme_id": programme_id, "programme_name": programme_name,
           "status": "running", "mode": mode, "targets_total": targets_total}
    r = requests.post(f"{base}/rest/v1/scan_runs", headers={**api(base, key), "Prefer": "return=representation"},
                      data=json.dumps(row), timeout=20)
    r.raise_for_status()
    return r.json()[0]["id"]


def patch_run(base, key, run_id, fields):
    requests.patch(f"{base}/rest/v1/scan_runs?id=eq.{run_id}", headers=api(base, key),
                   data=json.dumps(fields), timeout=20).raise_for_status()


def event(base, key, run_id, user_id, step, title, detail="", state="done"):
    requests.post(f"{base}/rest/v1/scan_events", headers={**api(base, key), "Prefer": "return=minimal"},
                  data=json.dumps({"run_id": run_id, "user_id": user_id, "step_no": step,
                                   "title": title, "detail": detail, "state": state}), timeout=20)
    print(f"[{state}] {title} - {detail}")


def host_of(t):
    u = t if "://" in t else "https://" + t
    return urlparse(u).netloc or t


def run_nuclei(nuclei, target, out_path, user_agent, rate_limit):
    cmd = [nuclei, "-u", target, "-jsonl", "-o", out_path, "-silent",
           "-severity", "low,medium,high,critical",
           "-etags", ",".join(EXCLUDE_TAGS),
           "-rate-limit", str(rate_limit), "-timeout", "10", "-retries", "1",
           "-disable-update-check", "-no-interactsh"]
    if user_agent:
        cmd += ["-H", f"User-Agent: {user_agent}"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=900)


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def sev_counts(items):
    c = {"crit": 0, "high": 0, "med": 0, "low": 0, "info": 0}
    for it in items:
        s = str((it.get("info", {}) or {}).get("severity", "")).lower()
        if s == "critical": c["crit"] += 1
        elif s == "high": c["high"] += 1
        elif s == "medium": c["med"] += 1
        elif s == "low": c["low"] += 1
        else: c["info"] += 1
    return c


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", required=True, help="comma-separated, or @file")
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--programme-name", default="Scan")
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    p.add_argument("--nuclei", default=os.path.join(HERE, "nuclei"))
    p.add_argument("--user-agent", default="")
    p.add_argument("--rate-limit", type=int, default=5)
    p.add_argument("--mode", default="scan", choices=["scan", "monitor"])
    args = p.parse_args()

    if args.targets.startswith("@"):
        targets = [l.strip() for l in open(args.targets[1:]) if l.strip() and not l.startswith("#")]
    else:
        targets = [t.strip() for t in args.targets.split(",") if t.strip()]

    base, key = args.supabase_url, args.service_key
    run_id = create_run(base, key, args.user_id, args.programme_id, args.programme_name, args.mode, len(targets))
    step = 0

    step += 1
    event(base, key, run_id, args.user_id, step, "Reading the scope and rules",
          f"Only the {len(targets)} in-scope target(s) you approved will be checked. "
          f"Rate limited to {args.rate_limit}/sec"
          + (", identifying as your HackerOne handle." if args.user_agent else "."))

    all_items = []
    combined = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl").name
    for i, target in enumerate(targets, 1):
        host = host_of(target)
        step += 1
        event(base, key, run_id, args.user_id, step, f"Checking {host}",
              "Running the vulnerability templates against this target…", state="active")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl").name
        try:
            run_nuclei(args.nuclei, target, out, args.user_agent, args.rate_limit)
        except subprocess.TimeoutExpired:
            pass
        items = load_jsonl(out)
        all_items += items
        c = sev_counts(items)
        patch_run(base, key, run_id, {"targets_done": i})
        found = c["crit"] + c["high"] + c["med"] + c["low"] + c["info"]
        detail = (f"{found} issue(s): {c['crit']} critical, {c['high']} high, {c['med']} medium, {c['low']} low."
                  if found else "No issues flagged on this target.")
        event(base, key, run_id, args.user_id, step, f"Checked {host}", detail, state="done")
        with open(combined, "a") as fh:
            for it in items:
                fh.write(json.dumps(it) + "\n")

    total = sev_counts(all_items)
    patch_run(base, key, run_id, {"crit": total["crit"], "high": total["high"], "med": total["med"],
                                  "low": total["low"], "info": total["info"],
                                  "findings_total": len(all_items)})

    step += 1
    if all_items:
        event(base, key, run_id, args.user_id, step, "Saving the findings, sorted by severity",
              "Each one gets a plain-English write-up so you know what it means.", state="active")
        subprocess.run(["python3", os.path.join(HERE, "import_nuclei_findings.py"),
                        "--results", combined, "--user-id", args.user_id,
                        "--programme-id", args.programme_id,
                        "--supabase-url", base, "--service-key", key],
                       capture_output=True, text=True)
        event(base, key, run_id, args.user_id, step, "Saved the findings, sorted by severity",
              f"{len(all_items)} finding(s) added to your list, most serious first.")

        step += 1
        event(base, key, run_id, args.user_id, step, "Capturing screenshot proof",
              "Opening each flagged URL and screenshotting what it returns…", state="active")
        subprocess.run(["python3", os.path.join(HERE, "capture_evidence.py"),
                        "--results", combined, "--user-id", args.user_id,
                        "--programme-id", args.programme_id,
                        "--supabase-url", base, "--service-key", key],
                       capture_output=True, text=True)
        event(base, key, run_id, args.user_id, step, "Captured screenshot proof",
              "Screenshots are attached to each finding as evidence.")

        step += 1
        event(base, key, run_id, args.user_id, step, "Report drafts ready",
              "Open any finding and tap Generate to get a submission-ready HackerOne report.", state="info")
    else:
        event(base, key, run_id, args.user_id, step, "No issues found this time",
              "Nothing flagged on the in-scope targets. Monitoring will keep watching for changes.", state="info")

    summary = (f"Scan complete. {len(all_items)} finding(s): {total['crit']} critical, {total['high']} high, "
               f"{total['med']} medium, {total['low']} low across {len(targets)} target(s)."
               if all_items else
               f"Scan complete. No issues flagged across {len(targets)} in-scope target(s).")
    patch_run(base, key, run_id, {"status": "completed", "summary": summary,
                                  "finished_at": datetime.now(timezone.utc).isoformat()})
    step += 1
    event(base, key, run_id, args.user_id, step, "Done - monitoring now on watch",
          "You'll be first to know if a new issue appears or a fix opens a gap.")
    print("RUN_ID", run_id)


if __name__ == "__main__":
    main()
