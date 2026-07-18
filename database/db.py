"""
SQLite database connection manager and helper base class for ScopeGuard AI.

All database access goes through the Database context manager or the
module-level get_db() helper, which returns a cached singleton connection.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional

# Default database path; overridden by settings at runtime.
DEFAULT_DB_PATH = Path("data/scopeguard.db")


class Database:
    """Thin wrapper around a sqlite3 connection with convenience helpers."""

    def __init__(self, path: Path | str = DEFAULT_DB_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the connection and configure it for use."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.path),
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self._conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent read performance.
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA foreign_keys=ON;")

    def close(self) -> None:
        """Close the connection if it is open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        assert self._conn is not None
        return self._conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Yield the connection inside an explicit transaction."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def execute(
        self, sql: str, params: tuple = ()
    ) -> sqlite3.Cursor:
        """Execute a statement and return the cursor."""
        return self.conn.execute(sql, params)

    def executemany(
        self, sql: str, params_seq: List[tuple]
    ) -> sqlite3.Cursor:
        """Execute a statement for each item in params_seq."""
        return self.conn.executemany(sql, params_seq)

    def fetchall(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Return all rows as a list of Row objects."""
        return self.conn.execute(sql, params).fetchall()

    def fetchone(
        self, sql: str, params: tuple = ()
    ) -> Optional[sqlite3.Row]:
        """Return a single Row or None."""
        return self.conn.execute(sql, params).fetchone()

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    # ------------------------------------------------------------------
    # Schema initialisation
    # ------------------------------------------------------------------

    def initialise(self) -> None:
        """Create all tables if they do not already exist."""
        from database.schema import CREATE_STATEMENTS

        with self.transaction():
            for statement in CREATE_STATEMENTS:
                self.conn.execute(statement)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_db_instance: Optional[Database] = None


def get_db(path: Path | str = DEFAULT_DB_PATH) -> Database:
    """Return a shared Database instance, creating it on first call."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(path)
        _db_instance.connect()
        _db_instance.initialise()
    return _db_instance


def reset_db() -> None:
    """Close and discard the singleton (used in tests)."""
    global _db_instance
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None
