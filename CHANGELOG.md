# Changelog

## 3.0.0 — Mobile Vercel application

### Added

- Mobile-first Next.js interface with responsive navigation and touch-friendly forms.
- Supabase email authentication, account confirmation and password-reset flow.
- PostgreSQL persistence with owner-aware composite foreign keys and row-level security.
- Vercel dashboards for programmes, assets, findings, evidence, reports, analysis, search, Daily Brief and settings.
- Markdown report downloads and installable mobile web-app manifest.
- Dedicated Vercel and Supabase deployment guide.

### Preserved

- The complete Streamlit and SQLite application remains available for local use.
- HexiStrike remains analysis-only and performs no target traffic or offensive actions.

## 2.0.0 — ScopeGuard AI, Sprints 1 and 2

### Added

- Transactional SQLite storage for programmes, assets, findings, evidence, reports, settings and activity history.
- Full programme, asset and finding lifecycle management.
- Structured evidence records with explicit redaction guidance.
- Editable report drafting and Markdown export.
- Dashboard metrics, severity and trend charts, programme health and recent activity.
- Daily Brief, global search, workflow progress and settings pages.
- Offline HexiStrike analysis helpers for prioritisation, evidence gaps, duplicate hints and report drafting.
- Idempotent migration of the original programme JSON.
- Automated tests for schema, transactions, CRUD, reporting, prioritisation and audit history.

### Changed

- Replaced the basic dashboard with a database-backed research overview.
- Connected the existing Review Queue to the central activity history.
- Preserved existing policy scripts and GitHub Actions safety gates.

### Security

- HexiStrike performs no scanning, exploitation, target traffic or autonomous offensive actions.
- Evidence UI warns against storing secrets and unnecessary personal data.
- Foreign keys, parameterised queries and transactional writes protect record integrity.
