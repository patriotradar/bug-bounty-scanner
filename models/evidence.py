"""Evidence model dataclass."""

from __future__ import annotations

EVIDENCE_TYPES = ["note", "url", "screenshot", "request", "response", "other"]


class Evidence:
    """Represents an evidence item attached to a finding."""

    def __init__(
        self,
        id: int,
        finding_id: int,
        evidence_type: str = "note",
        title: str = "",
        content: str = "",
        url: str = "",
        screenshot_path: str = "",
        request_data: str = "",
        response_data: str = "",
        created_at: str = "",
    ) -> None:
        self.id = id
        self.finding_id = finding_id
        self.evidence_type = evidence_type
        self.title = title
        self.content = content
        self.url = url
        self.screenshot_path = screenshot_path
        self.request_data = request_data
        self.response_data = response_data
        self.created_at = created_at

    @classmethod
    def from_row(cls, row: object) -> "Evidence":
        return cls(
            id=row["id"],
            finding_id=row["finding_id"],
            evidence_type=row["evidence_type"],
            title=row["title"],
            content=row["content"],
            url=row["url"],
            screenshot_path=row["screenshot_path"],
            request_data=row["request_data"],
            response_data=row["response_data"],
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "finding_id": self.finding_id,
            "evidence_type": self.evidence_type,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "screenshot_path": self.screenshot_path,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "created_at": self.created_at,
        }
