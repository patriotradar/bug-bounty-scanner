"""
Global Search — ScopeGuard AI

Search across programmes, findings and reports simultaneously.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Search — ScopeGuard AI",
    page_icon="🔎",
    layout="wide",
)

from database.db import get_db
from services.finding_service import FindingService
from services.programme_service import ProgrammeService
from services.report_service import ReportService
from models.finding import SEVERITIES, STATUSES
from utilities.helpers import severity_badge, status_badge, format_datetime

db = get_db()
find_svc = FindingService(db)
prog_svc = ProgrammeService(db)
rpt_svc = ReportService(db)

st.title("🔎 Global Search")
st.caption("Search across all programmes, findings and reports")
st.divider()

# ── Search bar ────────────────────────────────────────────────────────────────
query = st.text_input(
    "Search",
    placeholder="Enter a keyword, asset, CVE, title…",
    label_visibility="collapsed",
)

# ── Advanced filters (collapsed) ──────────────────────────────────────────────
with st.expander("Advanced Filters"):
    fc1, fc2, fc3, fc4 = st.columns(4)
    filter_severity = fc1.selectbox("Severity", ["All"] + SEVERITIES)
    filter_status = fc2.selectbox("Status", ["All"] + STATUSES)
    programmes = prog_svc.list_all()
    prog_options = {"All": None} | {p.name: p.id for p in programmes}
    filter_prog = fc3.selectbox("Programme", list(prog_options.keys()))
    filter_date = fc4.text_input("After date (YYYY-MM-DD)", placeholder="2024-01-01")

if not query.strip():
    st.info("Enter a search term above.")
    st.stop()

# ── Execute search ────────────────────────────────────────────────────────────
severity_arg = None if filter_severity == "All" else filter_severity
status_arg = None if filter_status == "All" else filter_status
prog_id_arg = prog_options.get(filter_prog)

found_findings = find_svc.list_all(
    programme_id=prog_id_arg,
    severity=severity_arg,
    status=status_arg,
    search=query.strip(),
)

found_programmes = prog_svc.search(query.strip())

# Filter reports by title/summary text
all_reports = rpt_svc.list_all()
q_lower = query.strip().lower()
found_reports = [
    r for r in all_reports
    if q_lower in r.title.lower()
    or q_lower in r.summary.lower()
    or q_lower in r.impact.lower()
]

# Apply date filter post-fetch if specified
if filter_date.strip():
    try:
        from datetime import date
        cutoff = filter_date.strip()
        found_findings = [f for f in found_findings if f.created_at >= cutoff]
        found_reports = [r for r in found_reports if r.created_at >= cutoff]
    except Exception:
        st.warning("Invalid date format. Use YYYY-MM-DD.")

# ── Results ────────────────────────────────────────────────────────────────────
total_results = len(found_findings) + len(found_programmes) + len(found_reports)
st.write(f"**{total_results} result(s)** for `{query}`")
st.divider()

# Findings results
if found_findings:
    st.subheader(f"🐛 Findings ({len(found_findings)})")
    for f in found_findings:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.write(f"**#{f.id}: {f.title}**")
            c2.write(severity_badge(f.severity))
            c3.write(status_badge(f.status))
            c4.caption(format_datetime(f.updated_at))
            if f.asset:
                st.caption(f"Asset: {f.asset}")
            if f.description:
                st.write(f.description[:200])

# Programme results
if found_programmes:
    st.subheader(f"🎯 Programmes ({len(found_programmes)})")
    for prog in found_programmes:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{prog.name}**")
            c2.caption(prog.platform or "No platform")
            c3.write("🟢 Active" if prog.enabled else "🔴 Disabled")
            if prog.scope_summary:
                st.write(prog.scope_summary[:200])

# Report results
if found_reports:
    st.subheader(f"📄 Reports ({len(found_reports)})")
    for rpt in found_reports:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**Report #{rpt.id}: {rpt.title}**")
            c2.caption(format_datetime(rpt.created_at))
            if rpt.summary:
                st.write(rpt.summary[:200])

if total_results == 0:
    st.info(f"No results found for `{query}`. Try a different search term.")
