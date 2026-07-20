"""
Findings — ScopeGuard AI

Full CRUD for vulnerability findings with filtering and workflow advancement.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Findings — ScopeGuard AI",
    page_icon="🐛",
    layout="wide",
)

from database.db import get_db
from services.finding_service import FindingService
from services.programme_service import ProgrammeService
from services.evidence_service import EvidenceService
from models.finding import SEVERITIES, STATUSES
from utilities.helpers import severity_badge, status_badge, format_datetime

db = get_db()
find_svc = FindingService(db)
prog_svc = ProgrammeService(db)
ev_svc = EvidenceService(db)

st.title("🐛 Findings")
st.caption("Manage vulnerability findings across all programmes")
st.divider()

# ── Sidebar: Filters & New Finding ────────────────────────────────────────────
with st.sidebar:
    st.subheader("🔎 Filter")
    programmes = prog_svc.list_all()
    prog_options = {"All": None} | {p.name: p.id for p in programmes}
    sel_prog_name = st.selectbox("Programme", list(prog_options.keys()))
    sel_prog_id = prog_options[sel_prog_name]

    sel_severity = st.selectbox("Severity", ["All"] + SEVERITIES)
    sel_status = st.selectbox("Status", ["All"] + STATUSES)
    search_query = st.text_input("Search", placeholder="Title, description, asset…")

    st.divider()
    st.subheader("➕ New Finding")
    with st.form("new_finding", clear_on_submit=True):
        f_title = st.text_input("Title *")
        f_desc = st.text_area("Description", height=80)
        f_prog = st.selectbox(
            "Programme",
            ["None"] + [p.name for p in programmes],
            key="nf_prog",
        )
        f_asset = st.text_input("Affected Asset")
        f_sev = st.selectbox("Severity", SEVERITIES, index=2)  # default medium
        f_notes = st.text_area("Notes", height=60)
        if st.form_submit_button("Create Finding", type="primary"):
            if not f_title.strip():
                st.error("Title is required.")
            else:
                prog_id = ""
                if f_prog != "None":
                    matched = [p for p in programmes if p.name == f_prog]
                    prog_id = matched[0].id if matched else ""
                finding = find_svc.create(
                    title=f_title.strip(),
                    description=f_desc.strip(),
                    programme_id=prog_id,
                    asset=f_asset.strip(),
                    severity=f_sev,
                    notes=f_notes.strip(),
                )
                st.success(f"Finding #{finding.id} created.")
                st.rerun()

# ── Apply filters ─────────────────────────────────────────────────────────────
findings = find_svc.list_all(
    programme_id=sel_prog_id,
    severity=None if sel_severity == "All" else sel_severity,
    status=None if sel_status == "All" else sel_status,
    search=search_query or None,
)

# ── Summary metrics ────────────────────────────────────────────────────────────
sev_counts = find_svc.count_by_severity()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total (filtered)", len(findings))
col2.metric("🔴 Critical", sev_counts.get("critical", 0))
col3.metric("🟠 High", sev_counts.get("high", 0))
col4.metric("🟡 Medium", sev_counts.get("medium", 0))
col5.metric("🔵 Low", sev_counts.get("low", 0))
st.divider()

# ── Findings table ────────────────────────────────────────────────────────────
if not findings:
    st.info("No findings match the current filters.")
    st.stop()

st.write(f"**{len(findings)} finding(s)**")

for finding in findings:
    ev_count = ev_svc.count_for_finding(finding.id)
    header = (
        f"{severity_badge(finding.severity)} — "
        f"**#{finding.id}: {finding.title}** "
        f"[{status_badge(finding.status)}]"
        f" · 📷 {ev_count}"
    )

    with st.expander(header):
        tab_view, tab_edit, tab_workflow, tab_delete = st.tabs(
            ["📋 Details", "✏️ Edit", "🔄 Workflow", "🗑️ Delete"]
        )

        # ── View ──────────────────────────────────────────────────────────────
        with tab_view:
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Severity:** {severity_badge(finding.severity)}")
            c2.write(f"**Status:** {status_badge(finding.status)}")
            c3.write(f"**Asset:** {finding.asset or '—'}")

            # Programme name
            prog_name = "—"
            if finding.programme_id:
                prog_obj = prog_svc.get(finding.programme_id)
                prog_name = prog_obj.name if prog_obj else finding.programme_id
            c1.write(f"**Programme:** {prog_name}")
            c2.write(f"**Created:** {format_datetime(finding.created_at)}")
            c3.write(f"**Updated:** {format_datetime(finding.updated_at)}")

            if finding.description:
                st.write("**Description:**")
                st.write(finding.description)
            if finding.notes:
                st.write("**Notes:**")
                st.write(finding.notes)

        # ── Edit ──────────────────────────────────────────────────────────────
        with tab_edit:
            with st.form(f"edit_finding_{finding.id}"):
                e_title = st.text_input("Title", value=finding.title)
                e_desc = st.text_area("Description", value=finding.description, height=100)
                prog_names = ["None"] + [p.name for p in programmes]
                cur_prog_name = next(
                    (p.name for p in programmes if p.id == finding.programme_id),
                    "None",
                )
                e_prog = st.selectbox("Programme", prog_names,
                                      index=prog_names.index(cur_prog_name) if cur_prog_name in prog_names else 0)
                e_asset = st.text_input("Affected Asset", value=finding.asset)
                e_sev = st.selectbox(
                    "Severity", SEVERITIES,
                    index=SEVERITIES.index(finding.severity) if finding.severity in SEVERITIES else 0,
                )
                e_status = st.selectbox(
                    "Status", STATUSES,
                    index=STATUSES.index(finding.status) if finding.status in STATUSES else 0,
                )
                e_notes = st.text_area("Notes", value=finding.notes, height=80)
                if st.form_submit_button("Save Changes", type="primary"):
                    new_prog_id = finding.programme_id
                    if e_prog != "None":
                        matched = [p for p in programmes if p.name == e_prog]
                        new_prog_id = matched[0].id if matched else finding.programme_id
                    elif e_prog == "None":
                        new_prog_id = ""
                    find_svc.update(
                        finding.id,
                        title=e_title.strip(),
                        description=e_desc.strip(),
                        programme_id=new_prog_id,
                        asset=e_asset.strip(),
                        severity=e_sev,
                        status=e_status,
                        notes=e_notes.strip(),
                    )
                    st.success("Finding updated.")
                    st.rerun()

        # ── Workflow ──────────────────────────────────────────────────────────
        with tab_workflow:
            st.write("**Investigation Workflow:**")
            workflow_steps = STATUSES
            current_idx = workflow_steps.index(finding.status) if finding.status in workflow_steps else 0

            cols = st.columns(len(workflow_steps))
            for i, step in enumerate(workflow_steps):
                with cols[i]:
                    if i < current_idx:
                        st.success(f"✅ {step}")
                    elif i == current_idx:
                        st.info(f"▶ {step}")
                    else:
                        st.write(f"⬜ {step}")

            st.divider()
            if finding.status != STATUSES[-1]:
                if st.button(
                    f"Advance → {STATUSES[min(current_idx + 1, len(STATUSES) - 1)]}",
                    key=f"advance_{finding.id}",
                    type="primary",
                ):
                    find_svc.advance_status(finding.id)
                    st.success("Status advanced.")
                    st.rerun()
            else:
                st.success("Finding is in final status: Closed.")

        # ── Delete ────────────────────────────────────────────────────────────
        with tab_delete:
            st.warning("Deleting a finding also removes its evidence.")
            if st.button(
                f"Delete Finding #{finding.id}",
                key=f"del_finding_{finding.id}",
                type="primary",
            ):
                find_svc.delete(finding.id)
                st.success(f"Finding #{finding.id} deleted.")
                st.rerun()
