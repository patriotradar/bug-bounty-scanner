"""Report generation service."""

from __future__ import annotations

from typing import List, Optional

from database.db import Database, get_db
from models.report import Report
from models.finding import Finding


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or get_db()

    def create(
        self,
        finding_id: int,
        title: str,
        summary: str = "",
        steps: str = "",
        expected_behaviour: str = "",
        actual_behaviour: str = "",
        impact: str = "",
        evidence_summary: str = "",
        remediation: str = "",
    ) -> Report:
        """Create a report for a finding and return it."""
        report = Report(
            id=0,
            finding_id=finding_id,
            title=title,
            summary=summary,
            steps=steps,
            expected_behaviour=expected_behaviour,
            actual_behaviour=actual_behaviour,
            impact=impact,
            evidence_summary=evidence_summary,
            remediation=remediation,
        )
        markdown = report.render_markdown()

        with self._db.transaction():
            cursor = self._db.execute(
                """
                INSERT INTO reports
                    (finding_id, title, summary, steps, expected_behaviour,
                     actual_behaviour, impact, evidence_summary, remediation,
                     markdown_export)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding_id, title, summary, steps, expected_behaviour,
                    actual_behaviour, impact, evidence_summary, remediation,
                    markdown,
                ),
            )
            rid = cursor.lastrowid

        result = self.get(rid)
        assert result is not None

        from history.logger import log
        log(
            event_type="report_generated",
            entity_type="report",
            entity_id=str(rid),
            description=f"Report generated: {title}",
            db=self._db,
        )
        return result

    def get(self, report_id: int) -> Optional[Report]:
        row = self._db.fetchone("SELECT * FROM reports WHERE id=?", (report_id,))
        return Report.from_row(row) if row else None

    def list_all(self) -> List[Report]:
        rows = self._db.fetchall(
            "SELECT * FROM reports ORDER BY created_at DESC"
        )
        return [Report.from_row(r) for r in rows]

    def list_for_finding(self, finding_id: int) -> List[Report]:
        rows = self._db.fetchall(
            "SELECT * FROM reports WHERE finding_id=? ORDER BY created_at DESC",
            (finding_id,),
        )
        return [Report.from_row(r) for r in rows]

    def update(
        self,
        report_id: int,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        steps: Optional[str] = None,
        expected_behaviour: Optional[str] = None,
        actual_behaviour: Optional[str] = None,
        impact: Optional[str] = None,
        evidence_summary: Optional[str] = None,
        remediation: Optional[str] = None,
    ) -> Optional[Report]:
        rpt = self.get(report_id)
        if rpt is None:
            return None

        rpt.title = title if title is not None else rpt.title
        rpt.summary = summary if summary is not None else rpt.summary
        rpt.steps = steps if steps is not None else rpt.steps
        rpt.expected_behaviour = expected_behaviour if expected_behaviour is not None else rpt.expected_behaviour
        rpt.actual_behaviour = actual_behaviour if actual_behaviour is not None else rpt.actual_behaviour
        rpt.impact = impact if impact is not None else rpt.impact
        rpt.evidence_summary = evidence_summary if evidence_summary is not None else rpt.evidence_summary
        rpt.remediation = remediation if remediation is not None else rpt.remediation
        rpt.markdown_export = ""  # will be regenerated
        new_markdown = rpt.render_markdown()

        with self._db.transaction():
            self._db.execute(
                """
                UPDATE reports
                SET title=?, summary=?, steps=?, expected_behaviour=?,
                    actual_behaviour=?, impact=?, evidence_summary=?,
                    remediation=?, markdown_export=?, updated_at=datetime('now')
                WHERE id=?
                """,
                (
                    rpt.title, rpt.summary, rpt.steps, rpt.expected_behaviour,
                    rpt.actual_behaviour, rpt.impact, rpt.evidence_summary,
                    rpt.remediation, new_markdown, report_id,
                ),
            )
        return self.get(report_id)

    def delete(self, report_id: int) -> bool:
        if self.get(report_id) is None:
            return False
        with self._db.transaction():
            self._db.execute("DELETE FROM reports WHERE id=?", (report_id,))
        return True

    def generate_from_finding(self, finding: Finding) -> Report:
        """Auto-generate a report draft from a finding's data."""
        from services.evidence_service import EvidenceService
        ev_service = EvidenceService(self._db)
        evidence_items = ev_service.list_for_finding(finding.id)

        evidence_lines = []
        for ev in evidence_items:
            label = ev.title or ev.evidence_type
            if ev.url:
                evidence_lines.append(f"- **{label}**: [{ev.url}]({ev.url})")
            elif ev.content:
                evidence_lines.append(f"- **{label}**: {ev.content[:120]}")
            else:
                evidence_lines.append(f"- {label}")
        evidence_summary = "\n".join(evidence_lines) or "_No evidence attached._"

        return self.create(
            finding_id=finding.id,
            title=f"{finding.title} — {finding.severity.capitalize()} Severity",
            summary=finding.description or f"A {finding.severity} severity finding on {finding.asset}.",
            steps="1. \n2. \n3. ",
            expected_behaviour="The application should handle this request securely.",
            actual_behaviour=finding.description or "Unexpected behaviour observed.",
            impact=f"Severity: {finding.severity.capitalize()}. Asset: {finding.asset}.",
            evidence_summary=evidence_summary,
            remediation="Review and harden the affected component.",
        )
