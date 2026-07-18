"""
Activity history logger.

The log() function is called by every service mutation to record
an immutable audit trail in the activity_history table.
"""

from __future__ import annotations

from typing import Optional

from database.db import Database, get_db


def log(
    event_type: str,
    description: str,
    entity_type: str = "",
    entity_id: str = "",
    db: Optional[Database] = None,
) -> None:
    """Append a single event to the activity_history table.

    This function is intentionally silent — if the write fails it will
    not crash the calling service.  History is best-effort.
    """
    _db = db or get_db()
    try:
        with _db.transaction():
            _db.execute(
                """
                INSERT INTO activity_history
                    (event_type, entity_type, entity_id, description)
                VALUES (?, ?, ?, ?)
                """,
                (event_type, entity_type, entity_id, description),
            )
    except Exception:
        # Never let logging break user operations.
        pass
