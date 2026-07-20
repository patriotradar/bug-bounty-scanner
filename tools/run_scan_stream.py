#!/usr/bin/env python3
"""
Streaming multi-host scan with a live activity feed.

Runs nuclei ONCE across a list of in-scope hosts (fast: template load cost is
paid once, and the global rate limit is honoured across the whole run), and
while it works it streams progress into scan_runs / scan_events so the
researcher watches findings appear live on the Scan Activity page. Then it
saves the findings, captures screenshot evidence, and marks the run complete.

Scope-safe: only the hosts in --list are touched, at --rate-limit req/sec total,
with the researcher's --user-agent on every request, excluding dos/intrusive/
bruteforce/fuzzing templates. Finds and proves; never exploits.
"""
import argparse
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_TAGS = "dos,fuzz,fuzzing,bruteforce,intrusive"
TAGS = ("exposure,exposures,config,files,env,git,svn,backup,logs,secret,disclosure,"
        "exposed-panel,exposed-panels,panel,default-login,takeover,kibana,grafana,"
        "elasticsearch,jenkins,jira,gitlab,springboot,debug,listing")


def api(base, key):
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def patch_run(base, key, run_id, fields):
    try:
        requests.patch(f"{base}/rest/v1/scan_runs?id=eq.{run_id}", headers=api(base, key),
                       data=json.dumps(fields), timeout=15)
    except Exception:
        pass


def event(base, key, run_id, user_id, step, title, detail="", state="done"):
    try:
        requests.post(f"{base}/rest/v1/scan_events", headers={**api(base, key), "Prefer": "return=minimal"},
                      data=json.dumps({"run_id": run_id, "user_id": user_id, "step_no": step,
                                       "title": title, "detail": detail, "state": state}), timeout=15)
    except Exception:
        pass
    print(f"[{state}] {title} - {detail}", flush=True)


def sev_of(it):
    return str((it.get("info", {}) or {}).get("severity", "")).lower()


def read_findings(path):
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


def counts(items):
    c = {"crit": 0, "high": 0, "med": 0, "low": 0, "info": 0}
    for it in items:
        s = sev_of(it)
        if s == "critical": c["crit"] += 1
        elif s == "high": c["high"] += 1
        elif s == "medium": c["med"] += 1
        elif s == "low": c["low"] += 1
        else: c["info"] += 1
    return c


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--programme-id", required=True)
    p.add_argument("--programme-name", default="Scan")
    p.add_argument("--supabase-url", required=True)
    p.add_argument("--service-key", required=True)
    p.add_argument("--nuclei", default=os.path.join(HERE, "nuclei"))
    p.add_argument("--user-agent", default="")
    p.add_argument("--rate-limit", type=int, default=5)
    p.add_argument("--tags", default=TAGS)
    args = p.parse_args()

    base, key = args.supabase_url, args.service_key
    hosts = [l.strip() for l in open(args.list) if l.strip() and not l.startswith("#")]
    n = len(hosts)

    row = {"user_id": args.user_id, "programme_id": args.programme_id, "programme_name": args.programme_name,
           "status": "running", "mode": "scan", "targets_total": n}
    r = requests.post(f"{base}/rest/v1/scan_runs", headers={**api(base, key), "Prefer": "return=representation"},
                      data=json.dumps(row), timeout=20)
    r.raise_for_status()
    run_id = r.json()[0]["id"]

    event(base, key, run_id, args.user_id, 1, "Reading the scope and rules",
          f"Only the {n} in-scope host(s) will be checked, at {args.rate_limit} requests/sec total"
          + (f", identifying as {args.user_agent}." if args.user_agent else "."))
    event(base, key, run_id, args.user_id, 2, f"Scanning {n} in-scope Acronis hosts",
          "Running the exposure, secret and open-panel checks. Findings will appear here as they're confirmed…",
          state="active")

    findings_file = f"/tmp/acronis_findings_{run_id}.jsonl"
    open(findings_file, "w").close()
    cmd = [args.nuclei, "-list", args.list, "-jsonl-export", findings_file,
           "-stats", "-stats-json", "-stats-interval", "5",
           "-severity", "low,medium,high,critical", "-tags", args.tags, "-etags", EXCLUDE_TAGS,
           "-rate-limit", str(args.rate_limit), "-timeout", "10", "-retries", "1",
           "-disable-update-check", "-no-interactsh"]
    if args.user_agent:
        cmd += ["-H", f"User-Agent: {args.user_agent}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    seen = set()
    step = 3
    done_pct = 0

    def watch_stats():
        nonlocal done_pct
        for line in proc.stderr:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                done_pct = int(float(s.get("percent", done_pct)))
            except (TypeError, ValueError):
                pass

    t = threading.Thread(target=watch_stats, daemon=True)
    t.start()

    # Poll findings + progress while nuclei runs.
    while proc.poll() is None:
        time.sleep(6)
        items = read_findings(findings_file)
        for it in items:
            sigkey = f"{it.get('template-id','')}|{it.get('matched-at','')}"
            if sigkey in seen:
                continue
            seen.add(sigkey)
            sev = sev_of(it) or "info"
            name = (it.get("info", {}) or {}).get("name") or it.get("template-id") or "Finding"
            where = it.get("matched-at") or it.get("host") or ""
            step += 1
            event(base, key, run_id, args.user_id, step, f"Found [{sev}] {name[:60]}",
                  f"On {where}", state=("warn" if sev in ("critical", "high") else "done"))
        c = counts(items)
        patch_run(base, key, run_id, {"crit": c["crit"], "high": c["high"], "med": c["med"],
                                      "low": c["low"], "info": c["info"], "findings_total": len(items),
                                      "targets_done": max(0, min(n, round(done_pct / 100 * n)))})

    # Final drain.
    items = read_findings(findings_file)
    for it in items:
        sigkey = f"{it.get('template-id','')}|{it.get('matched-at','')}"
        if sigkey in seen:
            continue
        seen.add(sigkey)
        sev = sev_of(it) or "info"
        name = (it.get("info", {}) or {}).get("name") or it.get("template-id") or "Finding"
        step += 1
        event(base, key, run_id, args.user_id, step, f"Found [{sev}] {name[:60]}",
              f"On {it.get('matched-at','')}", state=("warn" if sev in ("critical", "high") else "done"))
    c = counts(items)
    patch_run(base, key, run_id, {"crit": c["crit"], "high": c["high"], "med": c["med"], "low": c["low"],
                                  "info": c["info"], "findings_total": len(items), "targets_done": n})

    if items:
        step += 1
        event(base, key, run_id, args.user_id, step, "Saving the findings, sorted by severity",
              "Each gets a plain-English write-up. Remember: these still need confirming as real, in-scope bugs before reporting.",
              state="active")
        subprocess.run(["python3", os.path.join(HERE, "import_nuclei_findings.py"),
                        "--results", findings_file, "--user-id", args.user_id,
                        "--programme-id", args.programme_id, "--supabase-url", base, "--service-key", key],
                       capture_output=True, text=True)
        step += 1
        event(base, key, run_id, args.user_id, step, "Capturing screenshot proof",
              "Opening each flagged URL and screenshotting what it returns…", state="active")
        subprocess.run(["python3", os.path.join(HERE, "capture_evidence.py"),
                        "--results", findings_file, "--user-id", args.user_id,
                        "--programme-id", args.programme_id, "--supabase-url", base, "--service-key", key]
                       + (["--user-agent", args.user_agent] if args.user_agent else []),
                       capture_output=True, text=True)
        step += 1
        event(base, key, run_id, args.user_id, step, "Findings saved with screenshots",
              f"{len(items)} flagged item(s) added, most serious first. Review each before it becomes a report.", state="info")

    summary = (f"Scan complete. {len(items)} item(s) flagged across {n} hosts: "
               f"{c['crit']} critical, {c['high']} high, {c['med']} medium, {c['low']} low. "
               f"These are leads to confirm - not all will qualify."
               if items else
               f"Scan complete. Nothing flagged across {n} in-scope hosts this pass. Monitoring will keep watching.")
    patch_run(base, key, run_id, {"status": "completed", "summary": summary,
                                  "finished_at": datetime.now(timezone.utc).isoformat()})
    step += 1
    event(base, key, run_id, args.user_id, step, "Done - monitoring now on watch",
          "You'll be first to know if a new issue appears or a fix opens a gap.")
    print("RUN_ID", run_id, "findings", len(items), flush=True)


if __name__ == "__main__":
    main()
