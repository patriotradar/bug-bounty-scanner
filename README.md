# ScopeGuard AI

ScopeGuard AI is a professional, human-controlled workspace for organising authorised bug-bounty and security research. It manages programmes, scope assets, findings, evidence, reports and an audit timeline without autonomously testing or exploiting targets.

The repository now contains two connected implementations:

- A mobile-first Next.js application for Vercel, backed by a dedicated Supabase PostgreSQL database.
- The original Streamlit application for local Python use, backed by SQLite.

> Only work on assets for which you have current, explicit authorisation. Confirm programme rules at the source before every research session. ScopeGuard does not replace those rules.

## Features

- SQLite-backed Programme Manager with scope assets, enable/disable controls and review dates.
- Finding workflow: New → Investigating → Needs Evidence → Verified → Ready to Report → Submitted → Closed.
- Multiple structured evidence items per finding with redaction reminders.
- Editable reports with Markdown export.
- Dashboard, Daily Brief, programme health, severity charts and 30-day trends.
- Global search across programme, asset, severity, status and dates.
- Activity history for material record changes.
- HexiStrike offline analysis for evidence gaps, duplicate hints, transparent prioritisation and draft assistance.
- Preserved human Review Queue and existing policy gates.

HexiStrike is intentionally analysis-only. It never contacts a target, runs a scanner, selects an exploit or performs an offensive action.

## Installation

### Vercel/mobile application

Requires Node.js 20 or newer and a separate Supabase project.

```bash
npm install
cp .env.example .env.local
npm run dev
```

Run `supabase/migrations/001_scopeguard.sql` in the new Supabase project's SQL Editor, then enter its URL and publishable key in `.env.local`. See [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md) for the secure production checklist.

### Local Streamlit application

Requires Python 3.11 or newer.

```bash
git clone https://github.com/patriotradar/bug-bounty-scanner.git
cd bug-bounty-scanner
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/init_db.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Run Streamlit

```bash
python -m streamlit run streamlit/dashboard.py
```

Open the local URL printed by Streamlit. The sidebar connects the Dashboard, Review Queue, Daily Brief, Programmes, Findings, Evidence, Reports, Analysis, Global Search and Settings pages.

## Configuration

The default database is `data/scopeguard.db`. Override it before starting the application:

```bash
export SCOPEGUARD_DB_PATH=/absolute/path/to/scopeguard.db
```

The original `config/programmes.json` is imported idempotently on startup so the repository's existing programme configuration is preserved. It remains available for the original policy workflow, while the application uses SQLite as its operational store.

Never place passwords, API keys, session cookies, private keys or recovery codes in settings, evidence notes, JSON files or source control. Use the encrypted secret store of the eventual deployment platform for future integrations.

## Usage

1. Add or review an authorised programme and record its exact scope summary.
2. Add each in-scope asset and its type.
3. Record a manually identified finding and progress it through the workflow.
4. Attach safely redacted evidence.
5. Use Analysis to review evidence gaps, possible duplicates and work priority.
6. Generate a report draft, edit every field and export Markdown.
7. Record submission and closure only after the relevant human action occurs.

The Review Queue continues to record approval or rejection of proposed minimal verification. Approval is an audit decision only; the UI does not execute the proposal.

## Architecture

```text
app/             Streamlit entry point and connected pages
src/app/         Mobile-first Next.js pages used by Vercel
src/components/  Responsive application shell and shared UI
src/lib/         Supabase sessions, server actions and web types
supabase/        PostgreSQL schema and row-level security migration
database/        SQLite connection, schema and reusable repositories
models/          Shared choices and workflow definitions
services/        Programme, finding, evidence, reporting, search and dashboard logic
hexistrike/      Offline analysis, prioritisation and report assistance
reports/         Markdown rendering
history/         Central activity audit logger
utilities/       Bootstrap and reusable UI helpers
policy/          Existing verification safety policy
scripts/         Database setup and preserved policy utilities
tests/           Database, CRUD, reports, prioritisation and history tests
```

Business logic lives outside Streamlit pages. Services use parameterised SQLite queries, transactions, foreign keys and indexes. Material service changes write to `activity_history`.

## Tests

```bash
python -m pytest
python -m compileall app database models services hexistrike reports history utilities
python scripts/verify_policy.py --finding tests/sample-finding.json
```

For the Vercel application:

```bash
npm run typecheck
npm run build
```

The existing GitHub Actions dashboard and policy checks remain in place.

## Screenshots

Screenshots will be added after the first deployment visual QA pass:

- Dashboard overview
- Programme Manager
- Finding workflow
- Report editor
- HexiStrike analysis

## Sprint history

- **Original foundation:** programme JSON, approved-account guidance, review queue, policy scripts and lab workflow.
- **Sprint 1:** SQLite persistence, programme/assets CRUD, dashboard, Daily Brief, findings, evidence, reports, settings and audit history.
- **Sprint 2:** safe HexiStrike assistance, enhanced charts and health metrics, global search, complete workflow UI, responsive Streamlit components and automated tests.

See [CHANGELOG.md](CHANGELOG.md) for the file-level release summary.

## Roadmap

The proposed Sprint 3 covers authentication and roles, encrypted deployment configuration, read-only programme imports, protected evidence files, backups, user-defined report templates, accessibility and operational hardening. See [docs/SPRINT_3_ROADMAP.md](docs/SPRINT_3_ROADMAP.md).

## Safety and legal notice

This software is a workflow aid, not authorisation and not legal advice. Programme terms can change. The researcher is responsible for confirming scope, permitted methods, accounts, rate limits, data-handling rules and disclosure requirements before acting. Stop if unexpected personal data, secrets, an authentication boundary or an out-of-scope redirect is encountered.
