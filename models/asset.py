"""Asset model dataclass."""

from __future__ import annotations

ASSET_TYPES = ["domain", "wildcard", "api", "mobile", "ip", "other"]


class Asset:
    """Represents an in-scope asset belonging to a programme."""

    def __init__(
        self,
        id: int,
        programme_id: str,
        asset_type: str,
        value: str,
        wildcard: bool = False,
        notes: str = "",
        created_at: str = "",
    ) -> None:
        self.id = id
        self.programme_id = programme_id
        self.asset_type = asset_type
        self.value = value
        self.wildcard = wildcard
        self.notes = notes
        self.created_at = created_at

    @classmethod
    def from_row(cls, row: object) -> "Asset":
        return cls(
            id=row["id"],
            programme_id=row["programme_id"],
            asset_type=row["asset_type"],
            value=row["value"],
            wildcard=bool(row["wildcard"]),
            notes=row["notes"],
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "programme_id": self.programme_id,
            "asset_type": self.asset_type,
            "value": self.value,
            "wildcard": self.wildcard,
            "notes": self.notes,
            "created_at": self.created_at,
        }
