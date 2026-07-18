"""
Daily Brief — ScopeGuard AI

Shows:
  - Recent changes
  - Recent findings
  - Programmes requiring review
  - Reports awaiting completion
  - Activity timeline
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Daily Brief — ScopeGuard AI",
    page_icon="📋",
    layout="wide",
)

from database.db import get_db
from services.programme_service import ProgrammeService
from services.finding_service import FindingService
from services.activity_service import ActivityService
from services.report_service import ReportService
from utilities.helpers import severity_badge, status_badge, format_datetime

db = get_db()
prog_svc = ProgrammeService(db)
find_svc = FindingService(db)
act_svc = ActivityService(db)
rpt_svc = ReportService(db)

st.title("📋 Daily Brief")
st.caption("Your research overview for today")
st.divider()

# ── Summary metrics ───────────────────────────────────────────────────────────
all_findings = find_svc.list_all()
new_findings = [f for f in all_findings if f.status == "New"]
needs_evidence = [f for f in all_findings if f.status == "Needs Evidence"]
verified = [f for f in all_findings if f.status == "Verified"]
recent_findings = sorted(all_findings, key=lambda f: f.updated_at, reverse=True)[:5]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🆕 New Findings", len(new_findings))
col2.metric("📷 Needs Evidence", len(needs_evidence))
col3.metric("✅ Verified", len(verified))
col4.metric("📤 Ready to Report", len(verified))

st.divider()

# ── Programmes requiring review ────────────────────────────────────────────────
st.subheader("🎯 Programmes Requiring Attention")

programmes = prog_svc.list_all(enabled_only=True)
attention_needed = []
for prog in programmes:
    prog_findings = find_svc.list_all(programme_id=prog.id)
    crit = [f for f in prog_findings if f.severity == "critical" and f.status not in ("Submitted", "Closed")]
    high = [f for f in prog_findings if f.severity == "high" and f.status not in ("Submitted", "Closed")]
    unresolved = [f for f in prog_findings if f.status not in ("Submitted", "Closed")]
    if crit or high:
        attention_needed.append((prog, crit, high, unresolved))

if attention_needed:
    for prog, crit, high, unresolved in attention_needed:
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**{prog.name}**")
            c2.caption(prog.platform)
            c3.write(f"{len(unresolved)} unresolved findings")
            if crit:
                st.error(f"🔴 {len(crit)} critical finding(s) require immediate attention")
            if high:
                st.warning(f"🟠 {len(high)} high severity finding(s) open")
elif programmes:
    st.success("✅ No programmes currently require urgent attention.")
else:
    st.info("No active programmes. Add a programme to begin tracking.")

st.divider()

# ── Recent Findings ────────────────────────────────────────────────────────────
st.subheader("🐛 Recent Findings")

if recent_findings:
    for finding in recent_findings:
        with st.expander(
            f"{severity_badge(finding.severity)} — {finding.title} "
            f"[{status_badge(finding.status)}]"
        ):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Asset:** {finding.asset or '—'}")
            col2.write(f"**Status:** {status_badge(finding.status)}")
            col3.write(f"**Updated:** {format_datetime(finding.updated_at)}")
            if finding.description:
                st.write(finding.description[:300])
else:
    st.info("No findings yet. Go to **Findings** to record your first finding.")

st.divider()

# ── Reports Awaiting Completion ────────────────────────────────────────────────
st.subheader("📄 Reports Awaiting Completion")

verified_findings = find_svc.list_all(status="Verified")
if verified_findings:
    for finding in verified_findings:
        existing_reports = rpt_svc.list_for_finding(finding.id)
        if not existing_reports:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(
                    f"**{severity_badge(finding.severity)} — {finding.title}**"
                )
                col2.caption(f"Verified {format_datetime(finding.updated_at)}")
                st.caption("No report has been drafted for this finding yet.")
else:
    st.info("No verified findings awaiting reports.")

st.divider()

# ── Activity Timeline ──────────────────────────────────────────────────────────
st.subheader("📜 Activity Timeline (Last 20 Events)")

events = act_svc.list_recent(limit=20)
if events:
    for event in events:
        icon_map = {
            "programme_created": "🎯",
            "programme_updated": "✏️",
            "finding_created": "🐛",
            "finding_updated": "🔄",
            "evidence_added": "📷",
            "report_generated": "📄",
            "asset_added": "➕",
        }
        icon = icon_map.get(event.event_type, "📌")
        st.write(
            f"{icon} `{format_datetime(event.created_at)}` — {event.description}"
        )
else:
    st.info("No activity recorded yet.")
