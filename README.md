# 🛡️ ScopeGuard AI

> **Authorised bug bounty and security research management platform.**
> A human-controlled workflow tool — it never autonomously performs offensive testing or exploitation.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.47-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Tests](https://img.shields.io/badge/Tests-60%20passing-brightgreen)

---

## Overview

ScopeGuard AI is a professional, modular Streamlit application for managing authorised bug bounty and security research workflows. It helps you:

- Organise programmes and their in-scope assets
- Track vulnerability findings through an investigation workflow
- Attach and manage evidence per finding
- Draft and export professional vulnerability reports
- Analyse findings with HexiStrike (advisory only — no attacks)
- Maintain a complete audit trail

---

## Installation

### Prerequisites

- Python 3.12+
- pip

### Quick Start

```bash
git clone https://github.com/patriotradar/bug-bounty-scanner.git
cd bug-bounty-scanner

pip install -r app/requirements.txt

# Launch the dashboard
streamlit run app/dashboard.py --server.address 0.0.0.0 --server.port 8501
```

Or use the included shell script:

```bash
bash app/run_dashboard.sh
```

The SQLite database is created automatically at `data/scopeguard.db` on first run.

---

## Configuration

All settings are managed through the **⚙️ Settings** page in the UI, or directly in the `settings` table of the SQLite database.

| Setting | Default | Description |
|---|---|---|
| `app_name` | ScopeGuard AI | Display name |
| `theme` | dark | UI theme |
| `db_path` | data/scopeguard.db | Database file path |
| `reports_dir` | reports/ | Markdown export directory |
| `screenshots_dir` | data/screenshots/ | Screenshots directory |
| `github_actions_enabled` | false | GitHub Actions integration |

---

## Usage

### Navigation

| Page | Purpose |
|---|---|
| 🏠 Dashboard | Live statistics, charts, programme health, recent activity |
| 📋 Daily Brief | Today's priorities, pending reports, activity timeline |
| 🎯 Programmes | Create/edit/delete programmes and assets |
| 🐛 Findings | Full CRUD for vulnerability findings with workflow |
| 🔍 Evidence | Attach notes, URLs, screenshots, HTTP requests/responses |
| 📄 Reports | Generate, edit and export markdown reports |
| 🔎 Search | Global search across all data |
| ⚡ HexiStrike | AI-assisted analysis, prioritisation, duplicate detection |
| ⚙️ Settings | Application configuration |
| 📜 Activity History | Immutable audit log |
| ✅ Review Queue | Human-approval queue for verification proposals |

### Workflow

```
New → Investigating → Needs Evidence → Verified → Submitted → Closed
```

---

## Architecture

```
bug-bounty-scanner/
├── app/
│   ├── dashboard.py          # Main Streamlit entry point
│   ├── pages/                # Streamlit multi-page navigation
│   │   ├── 1_Daily_Brief.py
│   │   ├── 2_Programmes.py
│   │   ├── 3_Findings.py
│   │   ├── 4_Evidence.py
│   │   ├── 5_Reports.py
│   │   ├── 6_Search.py
│   │   ├── 7_Settings.py
│   │   ├── 8_Activity_History.py
│   │   ├── 9_HexiStrike.py
│   │   └── 10_Review_Queue.py
│   └── requirements.txt
├── database/
│   ├── db.py                 # Connection manager, query helpers
│   └── schema.py             # DDL CREATE statements
├── models/
│   ├── programme.py
│   ├── asset.py
│   ├── finding.py
│   ├── evidence.py
│   └── report.py
├── services/
│   ├── programme_service.py
│   ├── finding_service.py
│   ├── evidence_service.py
│   ├── report_service.py
│   ├── activity_service.py
│   └── settings_service.py
├── hexistrike/
│   ├── analysis.py           # Finding quality analysis, duplicate detection
│   ├── prioritiser.py        # Work queue prioritisation
│   └── report_helper.py      # Report drafting suggestions
├── history/
│   └── logger.py             # Immutable activity log writer
├── utilities/
│   └── helpers.py            # Shared formatters and badge helpers
├── tests/
│   ├── test_db.py
│   ├── test_crud.py
│   ├── test_reports.py
│   ├── test_prioritisation.py
│   └── test_history.py
├── config/                   # Legacy JSON config (preserved)
├── policy/                   # Policy rules (preserved)
├── data/                     # SQLite DB, action queue
├── CHANGELOG.md
└── README.md
```

---

## Testing

```bash
pip install pytest
pytest tests/ -v
```

60 tests covering database, CRUD, reports, HexiStrike analysis and history logging.

---

## Screenshots

_Screenshots placeholder — add after first deployment._

---

## Roadmap

### Sprint 3

- HackerOne / Bugcrowd API integration (read-only programme sync)
- Jira and Slack notification hooks
- Screenshot viewer embedded in Evidence page
- PDF report export
- Researcher notes with rich markdown editor
- Programme statistics and trends over time
- Import findings from Nuclei JSON output
- Two-factor confirmation for sensitive operations
- Dark/light theme switcher
- Docker deployment support

---

## Sprint History

| Sprint | Focus | Status |
|---|---|---|
| Sprint 1 | Database, Programme Manager, Findings, Evidence, Reports, Settings, Activity | ✅ Complete |
| Sprint 2 | HexiStrike, Dashboard improvements, Global Search, Workflow, UI Polish | ✅ Complete |
| Sprint 3 | API integrations, PDF export, Nuclei import, Docker | 🗓 Planned |

---

## Security Notice

ScopeGuard AI is a **workflow and analysis tool only**.

- It never autonomously performs offensive testing
- It never executes exploits or sends attack payloads
- All actions require explicit human review and approval
- Only test systems and assets you are explicitly authorised to test
- Never store credentials, session cookies or API tokens in the application

---

## Licence

MIT