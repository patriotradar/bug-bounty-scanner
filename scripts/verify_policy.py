#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def load_allowed_hosts(path):
    return {
        line.strip().lower()
        for line in Path(path).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--finding", required=True)
    parser.add_argument(
        "--policy",
        default="policy/verification-rules.json",
    )
    parser.add_argument(
        "--allowlist",
        default="policy/allowed-labs.txt",
    )

    args = parser.parse_args()

    with open(args.policy) as f:
        policy = json.load(f)

    with open(args.finding) as f:
        finding = json.load(f)

    host = (
        urlparse(
            finding.get("matched-at", "")
        ).hostname
        or ""
    ).lower()

    severity = (
        finding.get("info", {})
        .get("severity", "")
        .lower()
    )

    allowed_hosts = load_allowed_hosts(args.allowlist)

    if policy["mode"] != "lab-only":
        print("FAILED: policy not in lab mode")
        sys.exit(1)

    if host not in allowed_hosts:
        print(f"FAILED: {host} not approved")
        sys.exit(1)

    if severity not in policy["allowed_severities"]:
        print(f"FAILED: {severity} not approved")
        sys.exit(1)

    print("Verification approved")
    print(host)
    print(severity)


if __name__ == "__main__":
    main()