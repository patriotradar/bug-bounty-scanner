"""
HexiStrike Prioritiser — ranks findings to guide researcher workflow.

Never executes attacks. Advisory output only.
"""

from __future__ import annotations

from typing import List, Dict, Any

from models.finding import Finding

# Severity weights used for scoring
SEVERITY_WEIGHTS = {
    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
    "informational": 5,
}

# Status weights — findings that are further in the workflow score lower
# (already handled) or higher (need action)
STATUS_URGENCY = {
    "New": 30,
    "Investigating": 20,
    "Needs Evidence": 25,   # still needs work
    "Verified": 10,
    "Submitted": 5,
    "Closed": 0,
}


def _score_finding(finding: Finding) -> int:
    """Compute a priority score for a single finding."""
    severity_score = SEVERITY_WEIGHTS.get(finding.severity.lower(), 0)
    status_score = STATUS_URGENCY.get(finding.status, 0)
    return severity_score + status_score


def prioritise_findings(findings: List[Finding]) -> List[Dict[str, Any]]:
    """
    Return findings sorted by priority score (highest first).

    Each entry contains:
      - finding: the Finding object
      - score: integer priority score
      - priority_label: human-readable label (Critical / High / Medium / Low)
      - action: suggested next action for the researcher
    """

    def _label(score: int) -> str:
        if score >= 120:
            return "🔴 Critical Priority"
        if score >= 80:
            return "🟠 High Priority"
        if score >= 50:
            return "🟡 Medium Priority"
        return "🔵 Low Priority"

    def _action(finding: Finding) -> str:
        if finding.status == "New":
            return "Begin investigation — gather initial evidence."
        if finding.status == "Investigating":
            return "Collect request/response pair and screenshot."
        if finding.status == "Needs Evidence":
            return "Attach missing evidence before marking Verified."
        if finding.status == "Verified":
            return "Draft report and submit to programme."
        if finding.status == "Submitted":
            return "Await programme response; monitor for triage updates."
        return "No action required."

    scored = [
        {
            "finding": f,
            "score": _score_finding(f),
            "priority_label": _label(_score_finding(f)),
            "action": _action(f),
        }
        for f in findings
        if f.status != "Closed"  # Closed findings are deprioritised
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
