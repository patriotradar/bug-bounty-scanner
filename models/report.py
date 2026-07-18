"""Report model dataclass."""

from __future__ import annotations


class Report:
    """Represents a generated vulnerability report."""

    def __init__(
        self,
        id: int,
        finding_id: int,
        title: str,
        summary: str = "",
        steps: str = "",
        expected_behaviour: str = "",
        actual_behaviour: str = "",
        impact: str = "",
        evidence_summary: str = "",
        remediation: str = "",
        markdown_export: str = "",
        created_at: str = "",
        updated_at: str = "",
    ) -> None:
        self.id = id
        self.finding_id = finding_id
        self.title = title
        self.summary = summary
        self.steps = steps
        self.expected_behaviour = expected_behaviour
        self.actual_behaviour = actual_behaviour
        self.impact = impact
        self.evidence_summary = evidence_summary
        self.remediation = remediation
        self.markdown_export = markdown_export
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row: object) -> "Report":
        return cls(
            id=row["id"],
            finding_id=row["finding_id"] or 0,
            title=row["title"],
            summary=row["summary"],
            steps=row["steps"],
            expected_behaviour=row["expected_behaviour"],
            actual_behaviour=row["actual_behaviour"],
            impact=row["impact"],
            evidence_summary=row["evidence_summary"],
            remediation=row["remediation"],
            markdown_export=row["markdown_export"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "finding_id": self.finding_id,
            "title": self.title,
            "summary": self.summary,
            "steps": self.steps,
            "expected_behaviour": self.expected_behaviour,
            "actual_behaviour": self.actual_behaviour,
            "impact": self.impact,
            "evidence_summary": self.evidence_summary,
            "remediation": self.remediation,
            "markdown_export": self.markdown_export,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def render_markdown(self) -> str:
        """Return or regenerate the markdown representation of this report."""
        if self.markdown_export:
            return self.markdown_export

        lines = [
            f"# {self.title}",
            "",
            "## Summary",
            self.summary or "_No summary provided._",
            "",
            "## Steps to Reproduce",
            self.steps or "_No steps provided._",
            "",
            "## Expected Behaviour",
            self.expected_behaviour or "_Not specified._",
            "",
            "## Actual Behaviour",
            self.actual_behaviour or "_Not specified._",
            "",
            "## Impact",
            self.impact or "_Not assessed._",
            "",
            "## Evidence",
            self.evidence_summary or "_No evidence recorded._",
            "",
            "## Suggested Remediation",
            self.remediation or "_No remediation suggested._",
        ]
        return "\n".join(lines)
