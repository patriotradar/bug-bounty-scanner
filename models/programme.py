"""Programme model dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Programme:
    """Represents a bug bounty programme."""

    id: str
    name: str
    platform: str = ""
    enabled: bool = True
    notes: str = ""
    scope_summary: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: object) -> "Programme":
        """Create a Programme from a sqlite3.Row."""
        return cls(
            id=row["id"],
            name=row["name"],
            platform=row["platform"],
            enabled=bool(row["enabled"]),
            notes=row["notes"],
            scope_summary=row["scope_summary"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "enabled": self.enabled,
            "notes": self.notes,
            "scope_summary": self.scope_summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
