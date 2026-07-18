"""
Findings CRUD service.
"""

from __future__ import annotations

from typing import List, Optional

from database.db import Database, get_db
from models.finding import Finding


class FindingService:
    """Service for managing vulnerability findings."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()

    def create(
        self,
        title: str,
        description: str = "",
        programme_id: str = "",
        asset: str = "",
        severity: str = "low",
        status: str = "New",
        notes: str = "",
    ) -> Finding:
        """Create a new finding and return it."""
        with self._db.transaction():
            cursor = self._db.execute(
                """
                INSERT INTO findings
                    (title, description, programme_id, asset, severity, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, description, programme_id or None, asset, severity, status, notes),
            )
            fid = cursor.lastrowid

        finding = self.get(fid)
        assert finding is not None

        from history.logger import log
        log(
            event_type="finding_created",
            entity_type="finding",
            entity_id=str(fid),
            description=f"Finding created: {title} [{severity}]",
            db=self._db,
        )
        return finding

    def get(self, finding_id: int) -> Optional[Finding]:
        row = self._db.fetchone(
            "SELECT * FROM findings WHERE id=?", (finding_id,)
        )
        return Finding.from_row(row) if row else None

    def list_all(
        self,
        programme_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Finding]:
        """Return findings, with optional filters."""
        conditions = []
        params: list = []

        if programme_id:
            conditions.append("programme_id = ?")
            params.append(programme_id)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if search:
            like = f"%{search}%"
            conditions.append("(title LIKE ? OR description LIKE ? OR asset LIKE ?)")
            params.extend([like, like, like])

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = self._db.fetchall(
            f"SELECT * FROM findings {where} ORDER BY created_at DESC",
            tuple(params),
        )
        return [Finding.from_row(r) for r in rows]

    def update(
        self,
        finding_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        programme_id: Optional[str] = None,
        asset: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Finding]:
        finding = self.get(finding_id)
        if finding is None:
            return None

        new_title = title if title is not None else finding.title
        new_desc = description if description is not None else finding.description
        new_prog = programme_id if programme_id is not None else finding.programme_id
        new_asset = asset if asset is not None else finding.asset
        new_sev = severity if severity is not None else finding.severity
        new_status = status if status is not None else finding.status
        new_notes = notes if notes is not None else finding.notes

        with self._db.transaction():
            self._db.execute(
                """
                UPDATE findings
                SET title=?, description=?, programme_id=?, asset=?,
                    severity=?, status=?, notes=?, updated_at=datetime('now')
                WHERE id=?
                """,
                (
                    new_title, new_desc, new_prog or None, new_asset,
                    new_sev, new_status, new_notes, finding_id,
                ),
            )

        from history.logger import log
        log(
            event_type="finding_updated",
            entity_type="finding",
            entity_id=str(finding_id),
            description=f"Finding updated: {new_title} → {new_status}",
            db=self._db,
        )
        return self.get(finding_id)

    def delete(self, finding_id: int) -> bool:
        finding = self.get(finding_id)
        if finding is None:
            return False
        with self._db.transaction():
            self._db.execute("DELETE FROM findings WHERE id=?", (finding_id,))
        from history.logger import log
        log(
            event_type="finding_deleted",
            entity_type="finding",
            entity_id=str(finding_id),
            description=f"Finding deleted: {finding.title}",
            db=self._db,
        )
        return True

    def advance_status(self, finding_id: int) -> Optional[Finding]:
        """Move the finding to the next status in the workflow."""
        from models.finding import STATUSES
        finding = self.get(finding_id)
        if finding is None:
            return None
        try:
            idx = STATUSES.index(finding.status)
            next_status = STATUSES[min(idx + 1, len(STATUSES) - 1)]
        except ValueError:
            next_status = STATUSES[0]
        return self.update(finding_id, status=next_status)

    def count_by_severity(self) -> dict:
        """Return a dict of severity → count for all findings."""
        rows = self._db.fetchall(
            "SELECT severity, COUNT(*) as cnt FROM findings GROUP BY severity"
        )
        return {r["severity"]: r["cnt"] for r in rows}

    def count_by_status(self) -> dict:
        rows = self._db.fetchall(
            "SELECT status, COUNT(*) as cnt FROM findings GROUP BY status"
        )
        return {r["status"]: r["cnt"] for r in rows}
