"""
HexiStrike Analysis — static analysis helpers.

Analyses finding data to suggest missing evidence and flag quality issues.
This module is read-only and never executes any external action.
"""

from __future__ import annotations

from typing import List, Dict, Any

from models.finding import Finding
from models.evidence import Evidence


# Evidence types that are expected for verified findings
REQUIRED_EVIDENCE_TYPES = {"note", "url", "request", "response"}


def analyse_finding(
    finding: Finding, evidence: List[Evidence]
) -> Dict[str, Any]:
    """
    Analyse a finding and its evidence.

    Returns a dict with:
      - quality_score: 0-100 integer
      - missing_evidence: list of evidence types not yet present
      - suggestions: list of human-readable advisory strings
      - completeness: percentage of expected fields populated
    """
    suggestions: List[str] = []
    missing_evidence: List[str] = []

    # Check for missing description
    if not finding.description or len(finding.description) < 30:
        suggestions.append(
            "Add a detailed description explaining the vulnerability."
        )

    # Check for missing asset
    if not finding.asset:
        suggestions.append("Specify the affected asset (URL, endpoint, or host).")

    # Evaluate evidence coverage
    present_types = {ev.evidence_type for ev in evidence}
    for ev_type in REQUIRED_EVIDENCE_TYPES:
        if ev_type not in present_types:
            missing_evidence.append(ev_type)

    if not evidence:
        suggestions.append(
            "No evidence is attached. Add at least a request/response pair and a screenshot URL."
        )
    else:
        if "request" not in present_types:
            suggestions.append("Attach the raw HTTP request that triggers the issue.")
        if "response" not in present_types:
            suggestions.append("Attach the server response that confirms the issue.")
        if "screenshot" not in present_types and "url" not in present_types:
            suggestions.append("Add a screenshot or URL showing the impact.")

    # Check severity consistency
    if finding.severity == "critical" and finding.status in ("New", "Investigating"):
        suggestions.append(
            "Critical severity finding should be escalated to Verified or Submitted."
        )

    # Calculate quality score
    score = 100
    score -= len(missing_evidence) * 15   # -15 per missing evidence type
    score -= 20 if not finding.description or len(finding.description) < 30 else 0
    score -= 10 if not finding.asset else 0
    score -= 15 if not evidence else 0
    score = max(0, score)

    # Completeness: populated required fields
    required_fields = [finding.title, finding.description, finding.asset,
                       finding.severity, finding.programme_id]
    filled = sum(1 for f in required_fields if f and str(f).strip())
    completeness = int((filled / len(required_fields)) * 100)

    return {
        "quality_score": score,
        "missing_evidence": missing_evidence,
        "suggestions": suggestions,
        "completeness": completeness,
        "evidence_count": len(evidence),
    }


def detect_duplicates(
    target: Finding, candidates: List[Finding]
) -> List[Dict[str, Any]]:
    """
    Detect likely duplicate findings by comparing titles and assets.

    Returns a list of dicts with:
      - finding: the candidate Finding
      - similarity: a 0-100 similarity score
      - reason: explanation string
    """
    results = []

    def _token_overlap(a: str, b: str) -> float:
        """Simple token-overlap similarity between two strings."""
        tokens_a = set(a.lower().split())
        tokens_b = set(b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / len(union)

    for candidate in candidates:
        if candidate.id == target.id:
            continue

        reasons = []
        score = 0

        # Title similarity
        title_sim = _token_overlap(target.title, candidate.title)
        if title_sim >= 0.8:
            score += 60
            reasons.append(f"Very similar title ({int(title_sim * 100)}%)")
        elif title_sim >= 0.5:
            score += 30
            reasons.append(f"Similar title ({int(title_sim * 100)}%)")

        # Same asset
        if target.asset and candidate.asset and target.asset == candidate.asset:
            score += 20
            reasons.append("Same affected asset")

        # Same programme
        if (
            target.programme_id
            and candidate.programme_id
            and target.programme_id == candidate.programme_id
        ):
            score += 10
            reasons.append("Same programme")

        # Same severity
        if target.severity == candidate.severity:
            score += 10
            reasons.append("Same severity")

        if score >= 40:
            results.append({
                "finding": candidate,
                "similarity": min(score, 100),
                "reason": "; ".join(reasons),
            })

    # Sort by similarity descending
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results
