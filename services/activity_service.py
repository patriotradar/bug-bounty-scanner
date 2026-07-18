"""Activity History service."""

from __future__ import annotations

from typing import List, Optional

from database.db import Database, get_db


class ActivityEvent:
    """Lightweight wrapper around an activity_history row."""

    def __init__(self, row: object) -> None:
        self.id: int = row["id"]
        self.event_type: str = row["event_type"]
        self.entity_type: str = row["entity_type"]
        self.entity_id: str = row["entity_id"]
        self.description: str = row["description"]
        self.created_at: str = row["created_at"]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "description": self.description,
            "created_at": self.created_at,
        }


class ActivityService:
    """Service for reading activity history."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()

    def list_recent(self, limit: int = 50) -> List[ActivityEvent]:
        """Return the most recent activity events, newest first."""
        rows = self._db.fetchall(
            "SELECT * FROM activity_history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [ActivityEvent(r) for r in rows]

    def list_for_entity(self, entity_type: str, entity_id: str) -> List[ActivityEvent]:
        rows = self._db.fetchall(
            """
            SELECT * FROM activity_history
            WHERE entity_type=? AND entity_id=?
            ORDER BY created_at DESC
            """,
            (entity_type, entity_id),
        )
        return [ActivityEvent(r) for r in rows]

    def count(self) -> int:
        row = self._db.fetchone("SELECT COUNT(*) as cnt FROM activity_history")
        return row["cnt"] if row else 0
