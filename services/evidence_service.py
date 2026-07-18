"""Evidence CRUD service."""

from __future__ import annotations

from typing import List, Optional

from database.db import Database, get_db
from models.evidence import Evidence


class EvidenceService:
    """Service for managing evidence attached to findings."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()

    def add(
        self,
        finding_id: int,
        evidence_type: str = "note",
        title: str = "",
        content: str = "",
        url: str = "",
        screenshot_path: str = "",
        request_data: str = "",
        response_data: str = "",
    ) -> Evidence:
        """Add an evidence item to a finding."""
        with self._db.transaction():
            cursor = self._db.execute(
                """
                INSERT INTO evidence
                    (finding_id, evidence_type, title, content, url,
                     screenshot_path, request_data, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding_id, evidence_type, title, content, url,
                    screenshot_path, request_data, response_data,
                ),
            )
            eid = cursor.lastrowid

        ev = self.get(eid)
        assert ev is not None

        from history.logger import log
        log(
            event_type="evidence_added",
            entity_type="evidence",
            entity_id=str(eid),
            description=f"Evidence added to finding #{finding_id}: {title or evidence_type}",
            db=self._db,
        )
        return ev

    def get(self, evidence_id: int) -> Optional[Evidence]:
        row = self._db.fetchone(
            "SELECT * FROM evidence WHERE id=?", (evidence_id,)
        )
        return Evidence.from_row(row) if row else None

    def list_for_finding(self, finding_id: int) -> List[Evidence]:
        rows = self._db.fetchall(
            "SELECT * FROM evidence WHERE finding_id=? ORDER BY created_at",
            (finding_id,),
        )
        return [Evidence.from_row(r) for r in rows]

    def update(
        self,
        evidence_id: int,
        evidence_type: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        url: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        request_data: Optional[str] = None,
        response_data: Optional[str] = None,
    ) -> Optional[Evidence]:
        ev = self.get(evidence_id)
        if ev is None:
            return None

        with self._db.transaction():
            self._db.execute(
                """
                UPDATE evidence
                SET evidence_type=?, title=?, content=?, url=?,
                    screenshot_path=?, request_data=?, response_data=?
                WHERE id=?
                """,
                (
                    evidence_type or ev.evidence_type,
                    title if title is not None else ev.title,
                    content if content is not None else ev.content,
                    url if url is not None else ev.url,
                    screenshot_path if screenshot_path is not None else ev.screenshot_path,
                    request_data if request_data is not None else ev.request_data,
                    response_data if response_data is not None else ev.response_data,
                    evidence_id,
                ),
            )
        return self.get(evidence_id)

    def delete(self, evidence_id: int) -> bool:
        ev = self.get(evidence_id)
        if ev is None:
            return False
        with self._db.transaction():
            self._db.execute("DELETE FROM evidence WHERE id=?", (evidence_id,))
        return True

    def count_for_finding(self, finding_id: int) -> int:
        row = self._db.fetchone(
            "SELECT COUNT(*) as cnt FROM evidence WHERE finding_id=?",
            (finding_id,),
        )
        return row["cnt"] if row else 0
