"""
ScopeGuard AI — Main Dashboard

Displays live statistics, severity breakdown, programme health,
finding trends, and recent activity.
"""

import sys
from pathlib import Path

# Ensure the repo root is on the Python path so all modules are importable
# when Streamlit runs the app from the app/ subdirectory.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="ScopeGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import get_db
from services.programme_service import ProgrammeService
from services.finding_service import FindingService
from services.activity_service import ActivityService
from services.settings_service import SettingsService
from utilities.helpers import severity_badge, status_badge, format_datetime

# Initialise DB (creates tables on first run)
db = get_db()
prog_svc = ProgrammeService(db)
find_svc = FindingService(db)
act_svc = ActivityService(db)
settings = SettingsService(db)

app_name = settings.get("app_name", "ScopeGuard AI")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/ScopeGuard-AI-blue?style=for-the-badge", use_container_width=True)
    st.markdown("### 🛡️ ScopeGuard AI")
    st.caption("Authorised security research platform")
    st.divider()
    st.markdown(
        "**Navigation**\n"
        "- 🏠 Dashboard *(current)*\n"
        "- 📋 Daily Brief\n"
        "- 🎯 Programmes\n"
        "- 🐛 Findings\n"
        "- 🔍 Evidence\n"
        "- 📄 Reports\n"
        "- 🔎 Search\n"
        "- ⚙️ Settings\n"
        "- 📜 Activity History\n"
        "- ✅ Review Queue"
    )
    st.divider()
    st.caption("Use the sidebar pages above to navigate.")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛡️ ScopeGuard AI")
st.caption("Authorised bug bounty and security research management platform")
st.divider()

# ── Live Statistics ───────────────────────────────────────────────────────────
programmes = prog_svc.list_all()
active_programmes = [p for p in programmes if p.enabled]
all_findings = find_svc.list_all()
open_findings = [f for f in all_findings if f.status not in ("Closed", "Submitted")]
severity_counts = find_svc.count_by_severity()
status_counts = find_svc.count_by_status()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Programmes", len(programmes))
with col2:
    st.metric("Active Programmes", len(active_programmes))
with col3:
    st.metric("Total Findings", len(all_findings))
with col4:
    st.metric("Open Findings", len(open_findings))
with col5:
    pending_reports = status_counts.get("Verified", 0)
    st.metric("Pending Reports", pending_reports)

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 Findings by Severity")
    if severity_counts:
        from collections import OrderedDict
        ordered_sev = OrderedDict()
        for sev in ["critical", "high", "medium", "low", "informational"]:
            if sev in severity_counts:
                ordered_sev[severity_badge(sev)] = severity_counts[sev]
        if ordered_sev:
            st.bar_chart(ordered_sev)
        else:
            st.info("No findings recorded yet.")
    else:
        st.info("No findings recorded yet.")

with chart_col2:
    st.subheader("📈 Findings by Status")
    if status_counts:
        status_data = {
            status_badge(k): v
            for k, v in status_counts.items()
        }
        st.bar_chart(status_data)
    else:
        st.info("No findings recorded yet.")

st.divider()

# ── Programme Health ──────────────────────────────────────────────────────────
st.subheader("🎯 Programme Health")

if programmes:
    cols = st.columns(min(len(programmes), 4))
    for idx, prog in enumerate(programmes[:8]):
        col = cols[idx % len(cols)]
        with col:
            prog_findings = find_svc.list_all(programme_id=prog.id)
            open_count = sum(1 for f in prog_findings if f.status not in ("Closed", "Submitted"))
            crit_count = sum(1 for f in prog_findings if f.severity == "critical")
            with st.container(border=True):
                status_icon = "🟢" if prog.enabled else "🔴"
                st.write(f"**{status_icon} {prog.name}**")
                st.caption(prog.platform or "No platform")
                st.metric("Findings", len(prog_findings), delta=f"{open_count} open")
                if crit_count:
                    st.error(f"⚠️ {crit_count} critical")
else:
    st.info("No programmes configured. Go to **Programmes** to add your first programme.")

st.divider()

# ── Recent Activity ───────────────────────────────────────────────────────────
st.subheader("📜 Recent Activity")

recent = act_svc.list_recent(limit=10)
if recent:
    for event in recent:
        icon_map = {
            "programme_created": "🎯",
            "programme_updated": "✏️",
            "programme_deleted": "🗑️",
            "finding_created": "🐛",
            "finding_updated": "🔄",
            "finding_deleted": "🗑️",
            "evidence_added": "📷",
            "report_generated": "📄",
            "asset_added": "➕",
        }
        icon = icon_map.get(event.event_type, "📌")
        st.write(
            f"{icon} `{format_datetime(event.created_at)}` — {event.description}"
        )
else:
    st.info("No activity recorded yet. Start by creating a programme.")

st.divider()

# ── Safety Notice ─────────────────────────────────────────────────────────────
st.info(
    "🔒 **ScopeGuard AI** is a workflow and analysis platform. "
    "It never autonomously performs offensive testing or exploitation. "
    "All actions require explicit human approval."
)
