"""
Tests for the SQLite database layer.
"""

import sys
from pathlib import Path
import sqlite3
import tempfile
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import Database, reset_db
from database.schema import CREATE_STATEMENTS


@pytest.fixture
def tmp_db(tmp_path):
    """Return a fresh in-memory Database for each test."""
    db = Database(tmp_path / "test.db")
    db.connect()
    db.initialise()
    yield db
    db.close()


def test_database_connects(tmp_db):
    assert tmp_db.conn is not None


def test_tables_created(tmp_db):
    rows = tmp_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    table_names = {r["name"] for r in rows}
    expected = {
        "programmes", "assets", "findings",
        "evidence", "reports", "activity_history", "settings",
    }
    assert expected.issubset(table_names)


def test_fetchone_returns_none_on_miss(tmp_db):
    row = tmp_db.fetchone("SELECT * FROM programmes WHERE id='missing'")
    assert row is None


def test_transaction_rollback_on_error(tmp_db):
    with pytest.raises(Exception):
        with tmp_db.transaction():
            tmp_db.execute(
                "INSERT INTO programmes (id, name) VALUES (?, ?)",
                ("p1", "Test"),
            )
            raise RuntimeError("force rollback")
    # Row should not exist after rollback
    row = tmp_db.fetchone("SELECT * FROM programmes WHERE id='p1'")
    assert row is None


def test_foreign_key_cascade_delete(tmp_db):
    with tmp_db.transaction():
        tmp_db.execute(
            "INSERT INTO programmes (id, name) VALUES ('prog1', 'P1')"
        )
        tmp_db.execute(
            "INSERT INTO assets (programme_id, asset_type, value) VALUES ('prog1', 'domain', 'example.com')"
        )
    # Deleting the programme should cascade-delete the asset
    with tmp_db.transaction():
        tmp_db.execute("DELETE FROM programmes WHERE id='prog1'")
    assets = tmp_db.fetchall("SELECT * FROM assets WHERE programme_id='prog1'")
    assert len(assets) == 0
