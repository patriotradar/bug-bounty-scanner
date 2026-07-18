#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--results",
        required=True,
        help="Path to the Nuclei JSONL results file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the selected finding will be saved",
    )

    args = parser.parse_args()

    results_path = Path(args.results)
    output_path = Path(args.output)

    if not results_path.exists():
        raise SystemExit("FAILED: Nuclei results file was not found")

    findings = []

    with results_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                finding = json.loads(line)
                findings.append(finding)
            except json.JSONDecodeError as exc:
                print(
                    f"Skipping invalid JSON on line {line_number}: {exc}"
                )

    if not findings:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            json.dumps(
                {
                    "status": "no-findings",
                    "message": "No verification is required."
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        print("No findings were available for verification.")
        return

    severity_priority = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "info": 0,
        "unknown": -1,
    }

    def finding_priority(finding):
        severity = (
            finding.get("info", {})
            .get("severity", "unknown")
            .lower()
        )

        return severity_priority.get(severity, -1)

    findings.sort(
        key=finding_priority,
        reverse=True,
    )

    selected_finding = findings[0]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(
            selected_finding,
            indent=2,
        ),
        encoding="utf-8",
    )

    template_id = selected_finding.get(
        "template-id",
        "unknown",
    )

    matched_at = selected_finding.get(
        "matched-at",
        "unknown",
    )

    severity = (
        selected_finding.get("info", {})
        .get("severity", "unknown")
    )

    print("Finding prepared for review.")
    print(f"Template: {template_id}")
    print(f"Severity: {severity}")
    print(f"Matched at: {matched_at}")


if __name__ == "__main__":
    main()