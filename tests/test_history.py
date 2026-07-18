"""
Tests for activity history logging.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import Database
from history.logger import log
from services.activity_service import ActivityService
from services.programme_service import ProgrammeService
from services.finding_service import FindingService


@pytest.fixture
def db(tmp_path):
    _db = Database(tmp_path / "test.db")
    _db.connect()
    _db.initialise()
    yield _db
    _db.close()


@pytest.fixture
def act_svc(db):
    return ActivityService(db)


def test_manual_log(db, act_svc):
    log("test_event", "Manual log entry", entity_type="test", entity_id="t1", db=db)
    events = act_svc.list_recent(limit=10)
    assert any(e.event_type == "test_event" for e in events)


def test_log_does_not_raise_on_error():
    """log() should never raise even with a bad DB."""

    class BrokenDB:
        def transaction(self):
            from contextlib import contextmanager
            @contextmanager
            def _ctx():
                raise RuntimeError("broken")
                yield
            return _ctx()

    # Should complete without raising
    log("event", "desc", db=BrokenDB())


def test_programme_creation_logged(db, act_svc):
    prog_svc = ProgrammeService(db)
    prog_svc.create(name="Logged Programme", programme_id="lp1")
    events = act_svc.list_recent(limit=10)
    assert any("Logged Programme" in e.description for e in events)


def test_finding_creation_logged(db, act_svc):
    find_svc = FindingService(db)
    find_svc.create(title="Logged Finding", severity="high")
    events = act_svc.list_recent(limit=10)
    assert any("Logged Finding" in e.description for e in events)


def test_list_recent_newest_first(db, act_svc):
    for i in range(5):
        log("event", f"Event {i}", db=db)
    events = act_svc.list_recent(limit=5)
    # created_at should be descending (newest first)
    dates = [e.created_at for e in events]
    assert dates == sorted(dates, reverse=True)


def test_list_for_entity(db, act_svc):
    log("entity_event", "Entity desc", entity_type="finding", entity_id="99", db=db)
    log("other_event", "Other", entity_type="finding", entity_id="100", db=db)
    events = act_svc.list_for_entity("finding", "99")
    assert all(e.entity_id == "99" for e in events)


def test_activity_count(db, act_svc):
    initial = act_svc.count()
    log("count_test", "Testing count", db=db)
    assert act_svc.count() == initial + 1


def test_programme_update_logged(db, act_svc):
    prog_svc = ProgrammeService(db)
    prog_svc.create(name="UpdateMe", programme_id="um1")
    prog_svc.update("um1", name="UpdatedName")
    events = act_svc.list_recent(limit=20)
    assert any("UpdatedName" in e.description for e in events)
