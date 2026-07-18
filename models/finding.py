"""Finding model dataclass."""

from __future__ import annotations

SEVERITIES = ["critical", "high", "medium", "low", "informational"]

STATUSES = [
    "New",
    "Investigating",
    "Needs Evidence",
    "Verified",
    "Submitted",
    "Closed",
]


class Finding:
    """Represents a vulnerability finding."""

    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        programme_id: str = "",
        asset: str = "",
        severity: str = "low",
        status: str = "New",
        notes: str = "",
        created_at: str = "",
        updated_at: str = "",
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.programme_id = programme_id
        self.asset = asset
        self.severity = severity
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row: object) -> "Finding":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            programme_id=row["programme_id"] or "",
            asset=row["asset"],
            severity=row["severity"],
            status=row["status"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "programme_id": self.programme_id,
            "asset": self.asset,
            "severity": self.severity,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @property
    def severity_colour(self) -> str:
        """Return a hex colour for the severity badge."""
        colours = {
            "critical": "#9b2335",
            "high": "#c0392b",
            "medium": "#e67e22",
            "low": "#f1c40f",
            "informational": "#3498db",
        }
        return colours.get(self.severity.lower(), "#95a5a6")
