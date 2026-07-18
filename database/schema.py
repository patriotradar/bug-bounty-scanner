"""
DDL statements that create all ScopeGuard AI tables.

Tables:
  - programmes        Core programme records
  - assets            In-scope assets linked to programmes
  - findings          Vulnerability findings
  - evidence          Evidence items attached to findings
  - reports           Generated reports
  - activity_history  Immutable audit log
  - settings          Key-value application settings
"""

CREATE_STATEMENTS = [
    # ------------------------------------------------------------------
    # Programmes
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS programmes (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        platform    TEXT NOT NULL DEFAULT '',
        enabled     INTEGER NOT NULL DEFAULT 1,
        notes       TEXT NOT NULL DEFAULT '',
        scope_summary TEXT NOT NULL DEFAULT '',
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS assets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        programme_id TEXT NOT NULL REFERENCES programmes(id) ON DELETE CASCADE,
        asset_type  TEXT NOT NULL DEFAULT 'domain',
        value       TEXT NOT NULL,
        wildcard    INTEGER NOT NULL DEFAULT 0,
        notes       TEXT NOT NULL DEFAULT '',
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS findings (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        programme_id TEXT REFERENCES programmes(id) ON DELETE SET NULL,
        asset       TEXT NOT NULL DEFAULT '',
        severity    TEXT NOT NULL DEFAULT 'low',
        status      TEXT NOT NULL DEFAULT 'New',
        notes       TEXT NOT NULL DEFAULT '',
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS evidence (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id      INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
        evidence_type   TEXT NOT NULL DEFAULT 'note',
        title           TEXT NOT NULL DEFAULT '',
        content         TEXT NOT NULL DEFAULT '',
        url             TEXT NOT NULL DEFAULT '',
        screenshot_path TEXT NOT NULL DEFAULT '',
        request_data    TEXT NOT NULL DEFAULT '',
        response_data   TEXT NOT NULL DEFAULT '',
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS reports (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id          INTEGER REFERENCES findings(id) ON DELETE SET NULL,
        title               TEXT NOT NULL,
        summary             TEXT NOT NULL DEFAULT '',
        steps               TEXT NOT NULL DEFAULT '',
        expected_behaviour  TEXT NOT NULL DEFAULT '',
        actual_behaviour    TEXT NOT NULL DEFAULT '',
        impact              TEXT NOT NULL DEFAULT '',
        evidence_summary    TEXT NOT NULL DEFAULT '',
        remediation         TEXT NOT NULL DEFAULT '',
        markdown_export     TEXT NOT NULL DEFAULT '',
        created_at          TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Activity History
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS activity_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type  TEXT NOT NULL,
        entity_type TEXT NOT NULL DEFAULT '',
        entity_id   TEXT NOT NULL DEFAULT '',
        description TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS settings (
        key         TEXT PRIMARY KEY,
        value       TEXT NOT NULL DEFAULT '',
        description TEXT NOT NULL DEFAULT '',
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,

    # Indexes for common queries
    "CREATE INDEX IF NOT EXISTS idx_findings_programme ON findings(programme_id);",
    "CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);",
    "CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);",
    "CREATE INDEX IF NOT EXISTS idx_evidence_finding ON evidence(finding_id);",
    "CREATE INDEX IF NOT EXISTS idx_assets_programme ON assets(programme_id);",
    "CREATE INDEX IF NOT EXISTS idx_reports_finding ON reports(finding_id);",
    "CREATE INDEX IF NOT EXISTS idx_history_created ON activity_history(created_at DESC);",
]
