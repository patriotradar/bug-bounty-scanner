"""
HexiStrike Analysis — ScopeGuard AI

AI-assisted finding analysis, duplicate detection and prioritisation.
This page never executes attacks — advisory output only.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="HexiStrike — ScopeGuard AI",
    page_icon="⚡",
    layout="wide",
)

from database.db import get_db
from services.finding_service import FindingService
from services.evidence_service import EvidenceService
from hexistrike.analysis import analyse_finding, detect_duplicates
from hexistrike.prioritiser import prioritise_findings
from utilities.helpers import severity_badge, status_badge, format_datetime

db = get_db()
find_svc = FindingService(db)
ev_svc = EvidenceService(db)

st.title("⚡ HexiStrike Analysis")
st.caption("Advisory analysis to assist your research — no offensive actions performed")
st.info(
    "🔒 HexiStrike is purely analytical. It reads your existing findings and "
    "provides suggestions. It never sends requests, executes payloads, or "
    "performs any offensive action."
)
st.divider()

tab_priority, tab_analyse, tab_duplicates = st.tabs(
    ["📋 Prioritised Findings", "🔍 Finding Analysis", "🔁 Duplicate Detection"]
)

all_findings = find_svc.list_all()

# ── Prioritised Findings ──────────────────────────────────────────────────────
with tab_priority:
    st.subheader("📋 Prioritised Work Queue")

    if not all_findings:
        st.info("No findings yet.")
    else:
        prioritised = prioritise_findings(all_findings)
        if not prioritised:
            st.success("All findings are closed — nothing to prioritise.")
        else:
            for item in prioritised:
                f = item["finding"]
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
                    c1.write(f"**#{f.id}: {f.title}**")
                    c2.write(severity_badge(f.severity))
                    c3.write(status_badge(f.status))
                    c4.write(item["priority_label"])
                    st.caption(f"Score: {item['score']} · Action: {item['action']}")

# ── Finding Analysis ──────────────────────────────────────────────────────────
with tab_analyse:
    st.subheader("🔍 Analyse a Finding")

    if not all_findings:
        st.info("No findings to analyse.")
    else:
        finding_labels = {
            f"#{f.id}: {f.title} [{severity_badge(f.severity)}]": f.id
            for f in all_findings
        }
        sel = st.selectbox("Select Finding", list(finding_labels.keys()))
        sel_fid = finding_labels[sel]
        sel_finding = find_svc.get(sel_fid)

        if sel_finding:
            ev_items = ev_svc.list_for_finding(sel_finding.id)
            analysis = analyse_finding(sel_finding, ev_items)

            col1, col2, col3 = st.columns(3)
            col1.metric("Quality Score", f"{analysis['quality_score']}/100")
            col2.metric("Completeness", f"{analysis['completeness']}%")
            col3.metric("Evidence Items", analysis['evidence_count'])

            if analysis["missing_evidence"]:
                st.warning(
                    f"**Missing evidence types:** {', '.join(analysis['missing_evidence'])}"
                )

            if analysis["suggestions"]:
                st.subheader("💡 Suggestions")
                for suggestion in analysis["suggestions"]:
                    st.write(f"• {suggestion}")
            else:
                st.success("✅ This finding looks complete and well-documented.")

# ── Duplicate Detection ────────────────────────────────────────────────────────
with tab_duplicates:
    st.subheader("🔁 Detect Potential Duplicates")

    if len(all_findings) < 2:
        st.info("Need at least 2 findings to check for duplicates.")
    else:
        finding_labels = {
            f"#{f.id}: {f.title} [{severity_badge(f.severity)}]": f.id
            for f in all_findings
        }
        sel = st.selectbox(
            "Check finding for duplicates", list(finding_labels.keys()), key="dup_sel"
        )
        sel_fid = finding_labels[sel]
        sel_finding = find_svc.get(sel_fid)

        if sel_finding:
            duplicates = detect_duplicates(sel_finding, all_findings)
            if duplicates:
                st.warning(f"**{len(duplicates)} potential duplicate(s) found:**")
                for dup in duplicates:
                    df = dup["finding"]
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 2])
                        c1.write(f"**#{df.id}: {df.title}**")
                        c2.write(f"Similarity: **{dup['similarity']}%**")
                        c3.write(severity_badge(df.severity))
                        st.caption(f"Reason: {dup['reason']}")
            else:
                st.success("No likely duplicates detected for this finding.")
