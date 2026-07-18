# Changelog

All notable changes to ScopeGuard AI are documented here.

---

## Sprint 2 — 2026-07-18

### Added

**HexiStrike Module** (`hexistrike/`)
- `analysis.py` — Finding quality scoring, missing evidence detection, completeness calculation, potential duplicate detection using token-overlap similarity
- `prioritiser.py` — Work-queue prioritisation weighted by severity and workflow status; produces scored, labelled, actionable output
- `report_helper.py` — Report section drafting with severity-specific impact templates and vulnerability-class-matched remediation suggestions

**Dashboard Improvements** (`app/dashboard.py`)
- Live statistics: programme count, active count, total findings, open findings, pending reports
- Severity breakdown bar chart
- Finding status bar chart
- Programme health cards with per-programme finding counts and critical alerts
- Recent activity feed with event icons

**Global Search** (`app/pages/6_Search.py`)
- Search across programmes, findings and reports simultaneously
- Advanced filters: severity, status, programme, date cutoff

**HexiStrike Page** (`app/pages/9_HexiStrike.py`)
- Prioritised findings tab with scored work queue
- Finding analysis tab with quality score, completeness and suggestions
- Duplicate detection tab

**UI Improvements** (all pages)
- Professional sidebar navigation
- Tabbed layouts (Details / Edit / Workflow / Danger zones)
- Metric widgets, expanders, containers with borders
- Emoji severity and status badges
- Progress indicators on workflow tab

---

## Sprint 1 — 2026-07-18

### Added

**Database Layer** (`database/`)
- `db.py` — SQLite connection manager with WAL mode, foreign key enforcement, transaction context manager, fetchall/fetchone helpers, module-level singleton
- `schema.py` — DDL for 7 tables: programmes, assets, findings, evidence, reports, activity_history, settings; performance indexes

**Models** (`models/`)
- `Programme`, `Asset`, `Finding`, `Evidence`, `Report` dataclasses with `from_row()` and `to_dict()` methods
- `Finding.severity_colour` property for UI badges
- `Report.render_markdown()` for report export

**Services** (`services/`)
- `ProgrammeService` — Full CRUD, enable/disable, search, asset management
- `FindingService` — Full CRUD, multi-field filtering, status advancement, severity/status counts
- `EvidenceService` — Full CRUD for evidence items (notes, URLs, screenshots, HTTP pairs)
- `ReportService` — Report creation, CRUD, markdown export, auto-generation from finding
- `ActivityService` — Read recent events, entity-specific history, count
- `SettingsService` — Key/value settings with default seeding, bool helper

**History Logger** (`history/logger.py`)
- Silent best-effort activity logging called by all service mutations

**Utilities** (`utilities/helpers.py`)
- `severity_badge()`, `status_badge()`, `truncate()`, `format_datetime()`

**Pages** (`app/pages/`)
- `1_Daily_Brief.py` — Summary metrics, programme attention, recent findings, reports awaiting completion, activity timeline
- `2_Programmes.py` — Full programme manager with asset management, enable/disable, search, danger zone
- `3_Findings.py` — Full CRUD with workflow advancement, severity/status filtering, search
- `4_Evidence.py` — Evidence management per finding (all types)
- `5_Reports.py` — Report list with markdown export, report generator with HexiStrike suggestions
- `7_Settings.py` — General, database, directories, integrations, raw settings tabs
- `8_Activity_History.py` — Paginated audit log with event type filtering
- `10_Review_Queue.py` — Preserved original human-approval queue with activity logging integration

**Tests** (`tests/`)
- `test_db.py` — 5 tests: connection, table creation, fetchone, transaction rollback, foreign key cascade
- `test_crud.py` — 22 tests: programme, finding and evidence CRUD
- `test_reports.py` — 9 tests: report CRUD, markdown rendering, auto-generation
- `test_prioritisation.py` — 16 tests: prioritiser, analyser, duplicate detector, report helper
- `test_history.py` — 8 tests: log function, service-triggered logging, sort order, entity filter

**Total: 60 tests, all passing.**

### Changed

- `app/dashboard.py` — Replaced basic status check dashboard with full ScopeGuard AI dashboard
- `app/requirements.txt` — Added `pytest==8.3.5`
- `README.md` — Complete rewrite with installation, configuration, usage, architecture, roadmap

### Preserved

- `config/approved-accounts.json` — Original approved accounts config
- `config/programmes.json` — Original programmes config
- `policy/verification-rules.json` — Policy rules
- `policy/allowed-labs.txt` — Lab allowlist
- `data/action-queue.json` — Action queue
- `.github/workflows/` — All four GitHub Actions workflows
- `scripts/` — Policy verification scripts
- `targets.txt` — Target list

---

## Sprint 3 Roadmap

| Feature | Description |
|---|---|
| HackerOne API | Read-only programme sync from HackerOne platform |
| Bugcrowd API | Read-only programme sync from Bugcrowd platform |
| Jira Integration | Create Jira tickets from verified findings |
| Slack Notifications | Alert on new critical/high findings |
| PDF Export | Export reports as styled PDF documents |
| Screenshot Viewer | Inline screenshot viewer in Evidence page |
| Nuclei Import | Import findings from Nuclei JSON output files |
| Docker Support | Dockerfile and docker-compose for easy deployment |
| Rich Note Editor | Markdown editor for researcher notes |
| Programme Stats | Trend graphs per programme over time |
| Two-Factor Actions | Extra confirmation for irreversible operations |
| Theme Switcher | Live dark/light theme toggle |
