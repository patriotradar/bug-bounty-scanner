"""
Tests for the ReportService and Report model.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import Database
from services.finding_service import FindingService
from services.evidence_service import EvidenceService
from services.report_service import ReportService
from models.report import Report


@pytest.fixture
def db(tmp_path):
    _db = Database(tmp_path / "test.db")
    _db.connect()
    _db.initialise()
    yield _db
    _db.close()


@pytest.fixture
def find_svc(db):
    return FindingService(db)


@pytest.fixture
def ev_svc(db):
    return EvidenceService(db)


@pytest.fixture
def rpt_svc(db):
    return ReportService(db)


def test_create_report(find_svc, rpt_svc):
    f = find_svc.create(title="XSS", severity="high")
    rpt = rpt_svc.create(
        finding_id=f.id,
        title="XSS Report",
        summary="Cross-site scripting in login form.",
        steps="1. Submit payload\n2. Observe alert",
        expected_behaviour="Input should be sanitised",
        actual_behaviour="Script executed",
        impact="Session hijacking",
        evidence_summary="Screenshot attached",
        remediation="Encode output",
    )
    assert rpt.id > 0
    assert rpt.title == "XSS Report"
    assert rpt.finding_id == f.id


def test_get_report(find_svc, rpt_svc):
    f = find_svc.create(title="IDOR")
    rpt = rpt_svc.create(finding_id=f.id, title="IDOR Report")
    fetched = rpt_svc.get(rpt.id)
    assert fetched is not None
    assert fetched.title == "IDOR Report"


def test_update_report(find_svc, rpt_svc):
    f = find_svc.create(title="SSRF")
    rpt = rpt_svc.create(finding_id=f.id, title="SSRF Report")
    updated = rpt_svc.update(rpt.id, title="SSRF Updated", impact="Full SSRF impact")
    assert updated.title == "SSRF Updated"
    assert updated.impact == "Full SSRF impact"


def test_delete_report(find_svc, rpt_svc):
    f = find_svc.create(title="SQLi")
    rpt = rpt_svc.create(finding_id=f.id, title="SQLi Report")
    result = rpt_svc.delete(rpt.id)
    assert result is True
    assert rpt_svc.get(rpt.id) is None


def test_list_reports(find_svc, rpt_svc):
    f = find_svc.create(title="Multi Reports")
    rpt_svc.create(finding_id=f.id, title="Report 1")
    rpt_svc.create(finding_id=f.id, title="Report 2")
    all_rpts = rpt_svc.list_all()
    assert len(all_rpts) >= 2


def test_list_for_finding(find_svc, rpt_svc):
    f = find_svc.create(title="List For Finding")
    rpt_svc.create(finding_id=f.id, title="R1")
    rpt_svc.create(finding_id=f.id, title="R2")
    rpts = rpt_svc.list_for_finding(f.id)
    assert len(rpts) == 2


def test_render_markdown(find_svc, rpt_svc):
    f = find_svc.create(title="RenderMD")
    rpt = rpt_svc.create(
        finding_id=f.id,
        title="Markdown Test",
        summary="Summary here",
        steps="Step 1",
        impact="High impact",
        remediation="Fix it",
    )
    md = rpt.render_markdown()
    assert "# Markdown Test" in md
    assert "Summary here" in md
    assert "High impact" in md
    assert "Fix it" in md


def test_generate_from_finding(find_svc, ev_svc, rpt_svc):
    f = find_svc.create(
        title="Auto Report Test",
        severity="critical",
        asset="https://target.example.com/login",
        description="Critical auth bypass discovered.",
    )
    ev_svc.add(f.id, evidence_type="url", url="https://target.example.com/poc")
    rpt = rpt_svc.generate_from_finding(f)
    assert rpt.id > 0
    assert "Critical" in rpt.title
    assert rpt.finding_id == f.id
    assert "https://target.example.com/poc" in rpt.evidence_summary


def test_report_markdown_export_saved(find_svc, rpt_svc):
    f = find_svc.create(title="Export Test")
    rpt = rpt_svc.create(
        finding_id=f.id,
        title="Export",
        summary="Summary",
    )
    assert len(rpt.markdown_export) > 0
    assert "# Export" in rpt.markdown_export
