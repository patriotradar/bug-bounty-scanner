"""
Tests for CRUD services: Programme, Finding, Evidence.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import Database, reset_db
from services.programme_service import ProgrammeService
from services.finding_service import FindingService
from services.evidence_service import EvidenceService


@pytest.fixture
def db(tmp_path):
    _db = Database(tmp_path / "test.db")
    _db.connect()
    _db.initialise()
    yield _db
    _db.close()


@pytest.fixture
def prog_svc(db):
    return ProgrammeService(db)


@pytest.fixture
def find_svc(db):
    return FindingService(db)


@pytest.fixture
def ev_svc(db):
    return EvidenceService(db)


# ── Programme CRUD ────────────────────────────────────────────────────────────

def test_create_programme(prog_svc):
    prog = prog_svc.create(name="HackerOne Test", platform="HackerOne")
    assert prog.name == "HackerOne Test"
    assert prog.platform == "HackerOne"
    assert prog.enabled is True


def test_get_programme(prog_svc):
    prog = prog_svc.create(name="TestProg", programme_id="tp1")
    fetched = prog_svc.get("tp1")
    assert fetched is not None
    assert fetched.name == "TestProg"


def test_list_all_programmes(prog_svc):
    prog_svc.create(name="A")
    prog_svc.create(name="B")
    all_progs = prog_svc.list_all()
    assert len(all_progs) >= 2


def test_update_programme(prog_svc):
    prog = prog_svc.create(name="Original", programme_id="up1")
    updated = prog_svc.update("up1", name="Updated")
    assert updated is not None
    assert updated.name == "Updated"


def test_delete_programme(prog_svc):
    prog = prog_svc.create(name="ToDelete", programme_id="del1")
    result = prog_svc.delete("del1")
    assert result is True
    assert prog_svc.get("del1") is None


def test_enable_disable(prog_svc):
    prog = prog_svc.create(name="Toggle", programme_id="tog1", enabled=True)
    disabled = prog_svc.disable("tog1")
    assert disabled.enabled is False
    enabled = prog_svc.enable("tog1")
    assert enabled.enabled is True


def test_search_programmes(prog_svc):
    prog_svc.create(name="HackerOne Programme", platform="HackerOne", programme_id="h1")
    prog_svc.create(name="Bugcrowd Programme", platform="Bugcrowd", programme_id="b1")
    results = prog_svc.search("HackerOne")
    assert any(p.id == "h1" for p in results)
    assert all(p.id != "b1" for p in results)


def test_add_and_list_assets(prog_svc):
    prog_svc.create(name="AssetTest", programme_id="at1")
    asset = prog_svc.add_asset("at1", "domain", "example.com", wildcard=False)
    assert asset.value == "example.com"
    assets = prog_svc.list_assets("at1")
    assert len(assets) == 1


def test_delete_asset(prog_svc):
    prog_svc.create(name="ADelTest", programme_id="adt1")
    asset = prog_svc.add_asset("adt1", "api", "/api/v1", wildcard=False)
    result = prog_svc.delete_asset(asset.id)
    assert result is True
    assert prog_svc.get_asset(asset.id) is None


# ── Finding CRUD ──────────────────────────────────────────────────────────────

def test_create_finding(find_svc):
    f = find_svc.create(title="XSS in login", severity="high")
    assert f.id > 0
    assert f.title == "XSS in login"
    assert f.severity == "high"
    assert f.status == "New"


def test_get_finding(find_svc):
    f = find_svc.create(title="IDOR", severity="medium")
    fetched = find_svc.get(f.id)
    assert fetched is not None
    assert fetched.title == "IDOR"


def test_update_finding(find_svc):
    f = find_svc.create(title="Initial Title")
    updated = find_svc.update(f.id, title="Updated Title", status="Investigating")
    assert updated.title == "Updated Title"
    assert updated.status == "Investigating"


def test_delete_finding(find_svc):
    f = find_svc.create(title="Delete Me")
    result = find_svc.delete(f.id)
    assert result is True
    assert find_svc.get(f.id) is None


def test_advance_status(find_svc):
    f = find_svc.create(title="Workflow Test")
    assert f.status == "New"
    advanced = find_svc.advance_status(f.id)
    assert advanced.status == "Investigating"


def test_filter_findings_by_severity(find_svc):
    find_svc.create(title="High Finding", severity="high")
    find_svc.create(title="Low Finding", severity="low")
    high_findings = find_svc.list_all(severity="high")
    assert all(f.severity == "high" for f in high_findings)


def test_filter_findings_by_status(find_svc):
    f = find_svc.create(title="Status Filter")
    find_svc.update(f.id, status="Verified")
    verified = find_svc.list_all(status="Verified")
    assert any(x.id == f.id for x in verified)


def test_search_findings(find_svc):
    find_svc.create(title="SQL Injection on login", description="Classic sqli")
    find_svc.create(title="XSS in search box")
    results = find_svc.list_all(search="SQL Injection")
    assert any("SQL" in f.title for f in results)


def test_count_by_severity(find_svc):
    find_svc.create(title="C1", severity="critical")
    find_svc.create(title="C2", severity="critical")
    find_svc.create(title="H1", severity="high")
    counts = find_svc.count_by_severity()
    assert counts.get("critical", 0) >= 2
    assert counts.get("high", 0) >= 1


# ── Evidence CRUD ─────────────────────────────────────────────────────────────

def test_add_evidence(find_svc, ev_svc):
    f = find_svc.create(title="Evidence Test")
    ev = ev_svc.add(f.id, evidence_type="note", title="Initial Note", content="Test content")
    assert ev.id > 0
    assert ev.finding_id == f.id
    assert ev.content == "Test content"


def test_list_evidence_for_finding(find_svc, ev_svc):
    f = find_svc.create(title="Multi Evidence")
    ev_svc.add(f.id, evidence_type="url", url="https://example.com/poc")
    ev_svc.add(f.id, evidence_type="note", content="Observation note")
    items = ev_svc.list_for_finding(f.id)
    assert len(items) == 2


def test_update_evidence(find_svc, ev_svc):
    f = find_svc.create(title="Ev Update")
    ev = ev_svc.add(f.id, evidence_type="note", content="Before")
    updated = ev_svc.update(ev.id, content="After")
    assert updated.content == "After"


def test_delete_evidence(find_svc, ev_svc):
    f = find_svc.create(title="Ev Delete")
    ev = ev_svc.add(f.id, evidence_type="screenshot", screenshot_path="/tmp/s.png")
    result = ev_svc.delete(ev.id)
    assert result is True
    assert ev_svc.get(ev.id) is None
