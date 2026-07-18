"""
Programme and Asset CRUD service.

All mutations log activity via the ActivityService.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from database.db import Database, get_db
from models.programme import Programme
from models.asset import Asset


class ProgrammeService:
    """Service for managing bug bounty programmes and their assets."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()

    # ------------------------------------------------------------------
    # Programmes
    # ------------------------------------------------------------------

    def create(
        self,
        name: str,
        platform: str = "",
        enabled: bool = True,
        notes: str = "",
        scope_summary: str = "",
        programme_id: Optional[str] = None,
    ) -> Programme:
        """Insert a new programme and return it."""
        pid = programme_id or str(uuid.uuid4())[:8]
        with self._db.transaction():
            self._db.execute(
                """
                INSERT INTO programmes (id, name, platform, enabled, notes, scope_summary)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (pid, name, platform, int(enabled), notes, scope_summary),
            )
        prog = self.get(pid)
        assert prog is not None

        from history.logger import log
        log(
            event_type="programme_created",
            entity_type="programme",
            entity_id=pid,
            description=f"Programme created: {name}",
            db=self._db,
        )
        return prog

    def get(self, programme_id: str) -> Optional[Programme]:
        """Return a programme by its ID, or None if not found."""
        row = self._db.fetchone(
            "SELECT * FROM programmes WHERE id = ?", (programme_id,)
        )
        return Programme.from_row(row) if row else None

    def list_all(self, enabled_only: bool = False) -> List[Programme]:
        """Return all programmes, optionally filtered to enabled ones."""
        if enabled_only:
            rows = self._db.fetchall(
                "SELECT * FROM programmes WHERE enabled = 1 ORDER BY name"
            )
        else:
            rows = self._db.fetchall(
                "SELECT * FROM programmes ORDER BY name"
            )
        return [Programme.from_row(r) for r in rows]

    def search(self, query: str) -> List[Programme]:
        """Return programmes whose name or platform contains the query string."""
        like = f"%{query}%"
        rows = self._db.fetchall(
            """
            SELECT * FROM programmes
            WHERE name LIKE ? OR platform LIKE ? OR notes LIKE ?
            ORDER BY name
            """,
            (like, like, like),
        )
        return [Programme.from_row(r) for r in rows]

    def update(
        self,
        programme_id: str,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        enabled: Optional[bool] = None,
        notes: Optional[str] = None,
        scope_summary: Optional[str] = None,
    ) -> Optional[Programme]:
        """Update fields on an existing programme."""
        prog = self.get(programme_id)
        if prog is None:
            return None

        new_name = name if name is not None else prog.name
        new_platform = platform if platform is not None else prog.platform
        new_enabled = enabled if enabled is not None else prog.enabled
        new_notes = notes if notes is not None else prog.notes
        new_scope = scope_summary if scope_summary is not None else prog.scope_summary

        with self._db.transaction():
            self._db.execute(
                """
                UPDATE programmes
                SET name=?, platform=?, enabled=?, notes=?, scope_summary=?,
                    updated_at=datetime('now')
                WHERE id=?
                """,
                (new_name, new_platform, int(new_enabled), new_notes, new_scope, programme_id),
            )

        from history.logger import log
        log(
            event_type="programme_updated",
            entity_type="programme",
            entity_id=programme_id,
            description=f"Programme updated: {new_name}",
            db=self._db,
        )
        return self.get(programme_id)

    def delete(self, programme_id: str) -> bool:
        """Delete a programme and its assets (cascaded)."""
        prog = self.get(programme_id)
        if prog is None:
            return False
        with self._db.transaction():
            self._db.execute(
                "DELETE FROM programmes WHERE id=?", (programme_id,)
            )
        from history.logger import log
        log(
            event_type="programme_deleted",
            entity_type="programme",
            entity_id=programme_id,
            description=f"Programme deleted: {prog.name}",
            db=self._db,
        )
        return True

    def enable(self, programme_id: str) -> Optional[Programme]:
        return self.update(programme_id, enabled=True)

    def disable(self, programme_id: str) -> Optional[Programme]:
        return self.update(programme_id, enabled=False)

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    def add_asset(
        self,
        programme_id: str,
        asset_type: str,
        value: str,
        wildcard: bool = False,
        notes: str = "",
    ) -> Asset:
        """Add an asset to a programme and return the created Asset."""
        with self._db.transaction():
            cursor = self._db.execute(
                """
                INSERT INTO assets (programme_id, asset_type, value, wildcard, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (programme_id, asset_type, value, int(wildcard), notes),
            )
            asset_id = cursor.lastrowid

        asset = self.get_asset(asset_id)
        assert asset is not None

        from history.logger import log
        log(
            event_type="asset_added",
            entity_type="asset",
            entity_id=str(asset_id),
            description=f"Asset added to programme {programme_id}: {value}",
            db=self._db,
        )
        return asset

    def get_asset(self, asset_id: int) -> Optional[Asset]:
        row = self._db.fetchone("SELECT * FROM assets WHERE id=?", (asset_id,))
        return Asset.from_row(row) if row else None

    def list_assets(self, programme_id: str) -> List[Asset]:
        rows = self._db.fetchall(
            "SELECT * FROM assets WHERE programme_id=? ORDER BY asset_type, value",
            (programme_id,),
        )
        return [Asset.from_row(r) for r in rows]

    def update_asset(
        self,
        asset_id: int,
        asset_type: Optional[str] = None,
        value: Optional[str] = None,
        wildcard: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> Optional[Asset]:
        asset = self.get_asset(asset_id)
        if asset is None:
            return None

        new_type = asset_type if asset_type is not None else asset.asset_type
        new_value = value if value is not None else asset.value
        new_wildcard = wildcard if wildcard is not None else asset.wildcard
        new_notes = notes if notes is not None else asset.notes

        with self._db.transaction():
            self._db.execute(
                """
                UPDATE assets SET asset_type=?, value=?, wildcard=?, notes=?
                WHERE id=?
                """,
                (new_type, new_value, int(new_wildcard), new_notes, asset_id),
            )
        return self.get_asset(asset_id)

    def delete_asset(self, asset_id: int) -> bool:
        asset = self.get_asset(asset_id)
        if asset is None:
            return False
        with self._db.transaction():
            self._db.execute("DELETE FROM assets WHERE id=?", (asset_id,))
        return True
