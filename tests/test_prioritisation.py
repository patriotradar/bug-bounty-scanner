"""
Tests for HexiStrike prioritisation and analysis.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.finding import Finding
from models.evidence import Evidence
from hexistrike.prioritiser import prioritise_findings
from hexistrike.analysis import analyse_finding, detect_duplicates
from hexistrike.report_helper import suggest_report_sections


def _make_finding(id, title, severity="medium", status="New", asset="example.com", description="", programme_id=""):
    return Finding(
        id=id,
        title=title,
        severity=severity,
        status=status,
        asset=asset,
        description=description,
        programme_id=programme_id,
    )


def _make_evidence(id, finding_id, evidence_type="note", content="", url=""):
    return Evidence(
        id=id,
        finding_id=finding_id,
        evidence_type=evidence_type,
        content=content,
        url=url,
    )


# ── Prioritiser ───────────────────────────────────────────────────────────────

def test_prioritise_empty():
    assert prioritise_findings([]) == []


def test_critical_ranked_first():
    findings = [
        _make_finding(1, "Low Finding", severity="low"),
        _make_finding(2, "Critical Finding", severity="critical"),
        _make_finding(3, "Medium Finding", severity="medium"),
    ]
    result = prioritise_findings(findings)
    assert result[0]["finding"].severity == "critical"


def test_closed_findings_excluded():
    findings = [
        _make_finding(1, "Closed", severity="critical", status="Closed"),
        _make_finding(2, "Open High", severity="high", status="New"),
    ]
    result = prioritise_findings(findings)
    assert all(item["finding"].status != "Closed" for item in result)


def test_priority_labels_present():
    findings = [_make_finding(1, "Test", severity="high")]
    result = prioritise_findings(findings)
    assert "priority_label" in result[0]
    assert "action" in result[0]


def test_needs_evidence_action():
    findings = [_make_finding(1, "Needs Ev", status="Needs Evidence")]
    result = prioritise_findings(findings)
    assert "evidence" in result[0]["action"].lower()


# ── Analysis ──────────────────────────────────────────────────────────────────

def test_analyse_no_evidence():
    f = _make_finding(1, "No Evidence Finding", description="A detailed description that is long enough to pass.")
    result = analyse_finding(f, [])
    assert result["evidence_count"] == 0
    assert "note" in result["missing_evidence"]
    assert result["quality_score"] < 100


def test_analyse_complete_finding():
    f = _make_finding(
        1,
        "Complete Finding",
        description="A sufficiently detailed description of the vulnerability found.",
        asset="https://target.example.com",
    )
    evidence = [
        _make_evidence(1, 1, "note", content="Observation"),
        _make_evidence(2, 1, "url", url="https://target.example.com/poc"),
        _make_evidence(3, 1, "request", content="GET /poc HTTP/1.1"),
        _make_evidence(4, 1, "response", content="HTTP/1.1 200 OK"),
    ]
    result = analyse_finding(f, evidence)
    assert result["missing_evidence"] == []
    assert result["quality_score"] == 100


def test_analyse_missing_asset():
    f = _make_finding(1, "No Asset", asset="", description="A very detailed description indeed.")
    result = analyse_finding(f, [])
    assert any("asset" in s.lower() for s in result["suggestions"])


def test_completeness_percentage():
    f = _make_finding(
        1, "Full", asset="example.com",
        description="Full description", programme_id="p1",
    )
    result = analyse_finding(f, [])
    assert result["completeness"] == 100


# ── Duplicate Detection ───────────────────────────────────────────────────────

def test_no_duplicates_when_unrelated():
    target = _make_finding(1, "SQL Injection on login", asset="login.example.com")
    others = [
        _make_finding(2, "XSS in search", asset="search.example.com"),
        _make_finding(3, "CSRF on profile", asset="profile.example.com"),
    ]
    result = detect_duplicates(target, others)
    assert len(result) == 0


def test_duplicate_detected():
    target = _make_finding(1, "SQL injection on login page", asset="login.example.com", severity="high")
    duplicate = _make_finding(2, "SQL injection on login page", asset="login.example.com", severity="high")
    result = detect_duplicates(target, [duplicate])
    assert len(result) >= 1
    assert result[0]["similarity"] >= 80


def test_target_not_in_its_own_duplicates():
    target = _make_finding(1, "XSS vulnerability", asset="app.example.com")
    result = detect_duplicates(target, [target])
    assert len(result) == 0


# ── Report Helper ─────────────────────────────────────────────────────────────

def test_suggest_report_sections_keys():
    f = _make_finding(1, "XSS Issue", severity="high", asset="https://app.example.com")
    sections = suggest_report_sections(f, [])
    assert "title" in sections
    assert "summary" in sections
    assert "steps" in sections
    assert "impact" in sections
    assert "remediation" in sections


def test_xss_remediation_suggested():
    f = _make_finding(1, "Reflected XSS", severity="high", description="Cross-site scripting found")
    sections = suggest_report_sections(f, [])
    assert "escaping" in sections["remediation"].lower() or "csp" in sections["remediation"].lower()


def test_sql_injection_remediation_suggested():
    f = _make_finding(1, "SQL injection on search", severity="critical")
    sections = suggest_report_sections(f, [])
    assert "parameterised" in sections["remediation"].lower() or "prepared" in sections["remediation"].lower()


def test_evidence_included_in_suggestions():
    f = _make_finding(1, "Test", severity="medium")
    ev = [_make_evidence(1, 1, "url", url="https://poc.example.com")]
    sections = suggest_report_sections(f, ev)
    assert "https://poc.example.com" in sections["evidence_summary"]
