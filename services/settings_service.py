"""Settings service — key/value store backed by SQLite."""

from __future__ import annotations

from typing import Optional

from database.db import Database, get_db

# Default settings seeded on first run
DEFAULTS = {
    "theme": ("dark", "UI theme (dark or light)"),
    "db_path": ("data/scopeguard.db", "Path to the SQLite database file"),
    "reports_dir": ("reports/", "Directory for exported markdown reports"),
    "screenshots_dir": ("data/screenshots/", "Directory for screenshot files"),
    "github_actions_enabled": ("false", "Enable GitHub Actions integration"),
    "app_name": ("ScopeGuard AI", "Application display name"),
}


class SettingsService:
    """CRUD service for application settings."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        """Insert default values for any settings that do not yet exist."""
        with self._db.transaction():
            for key, (value, description) in DEFAULTS.items():
                self._db.execute(
                    """
                    INSERT OR IGNORE INTO settings (key, value, description)
                    VALUES (?, ?, ?)
                    """,
                    (key, value, description),
                )

    def get(self, key: str, fallback: str = "") -> str:
        row = self._db.fetchone(
            "SELECT value FROM settings WHERE key=?", (key,)
        )
        return row["value"] if row else fallback

    def set(self, key: str, value: str) -> None:
        with self._db.transaction():
            self._db.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                    updated_at=datetime('now')
                """,
                (key, value),
            )

    def list_all(self) -> list:
        rows = self._db.fetchall("SELECT * FROM settings ORDER BY key")
        return [dict(r) for r in rows]

    def get_bool(self, key: str, fallback: bool = False) -> bool:
        val = self.get(key, str(fallback)).lower()
        return val in ("true", "1", "yes", "on")
