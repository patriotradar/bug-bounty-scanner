"""
Evidence — ScopeGuard AI

Manage evidence items attached to findings.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Evidence — ScopeGuard AI",
    page_icon="🔍",
    layout="wide",
)

from database.db import get_db
from services.finding_service import FindingService
from services.evidence_service import EvidenceService
from models.evidence import EVIDENCE_TYPES
from utilities.helpers import severity_badge, format_datetime

db = get_db()
find_svc = FindingService(db)
ev_svc = EvidenceService(db)

st.title("🔍 Evidence")
st.caption("Manage evidence attached to your findings")
st.divider()

# ── Sidebar: Select Finding ────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("📌 Select Finding")
    all_findings = find_svc.list_all()
    if not all_findings:
        st.info("No findings yet.")
    else:
        finding_labels = {
            f"#{f.id}: {f.title[:40]} [{f.severity}]": f.id
            for f in all_findings
        }
        selected_label = st.selectbox("Finding", list(finding_labels.keys()))
        selected_finding_id = finding_labels[selected_label]

        st.divider()
        st.subheader("➕ Add Evidence")
        with st.form("add_evidence", clear_on_submit=True):
            ev_type = st.selectbox("Type", EVIDENCE_TYPES)
            ev_title = st.text_input("Title")
            ev_content = st.text_area("Content / Note", height=80)
            ev_url = st.text_input("URL")
            ev_screenshot = st.text_input("Screenshot Path")
            ev_request = st.text_area("HTTP Request", height=80)
            ev_response = st.text_area("HTTP Response", height=80)
            if st.form_submit_button("Add Evidence", type="primary"):
                ev_svc.add(
                    finding_id=selected_finding_id,
                    evidence_type=ev_type,
                    title=ev_title.strip(),
                    content=ev_content.strip(),
                    url=ev_url.strip(),
                    screenshot_path=ev_screenshot.strip(),
                    request_data=ev_request.strip(),
                    response_data=ev_response.strip(),
                )
                st.success("Evidence added.")
                st.rerun()

if not all_findings:
    st.info("No findings yet. Create a finding first.")
    st.stop()

# ── Finding context ────────────────────────────────────────────────────────────
finding = find_svc.get(selected_finding_id)
if not finding:
    st.error("Finding not found.")
    st.stop()

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Finding #{finding.id}:** {finding.title}")
    c2.write(f"**Severity:** {severity_badge(finding.severity)}")
    c3.write(f"**Asset:** {finding.asset or '—'}")

st.divider()

# ── Evidence list ──────────────────────────────────────────────────────────────
evidence_items = ev_svc.list_for_finding(finding.id)

st.subheader(f"📷 Evidence ({len(evidence_items)} item(s))")

if not evidence_items:
    st.info("No evidence attached yet. Use the sidebar to add evidence.")
else:
    for ev in evidence_items:
        with st.expander(
            f"**{ev.evidence_type.upper()}** — "
            f"{ev.title or '(no title)'} "
            f"· {format_datetime(ev.created_at)}"
        ):
            tab_view, tab_edit, tab_delete = st.tabs(["📋 View", "✏️ Edit", "🗑️ Delete"])

            with tab_view:
                if ev.content:
                    st.write("**Content:**")
                    st.write(ev.content)
                if ev.url:
                    st.write(f"**URL:** [{ev.url}]({ev.url})")
                if ev.screenshot_path:
                    st.write(f"**Screenshot:** `{ev.screenshot_path}`")
                if ev.request_data:
                    st.write("**HTTP Request:**")
                    st.code(ev.request_data, language="http")
                if ev.response_data:
                    st.write("**HTTP Response:**")
                    st.code(ev.response_data, language="http")
                if not any([ev.content, ev.url, ev.screenshot_path, ev.request_data, ev.response_data]):
                    st.caption("No content recorded for this evidence item.")

            with tab_edit:
                with st.form(f"edit_ev_{ev.id}"):
                    edit_type = st.selectbox(
                        "Type", EVIDENCE_TYPES,
                        index=EVIDENCE_TYPES.index(ev.evidence_type) if ev.evidence_type in EVIDENCE_TYPES else 0,
                    )
                    edit_title = st.text_input("Title", value=ev.title)
                    edit_content = st.text_area("Content", value=ev.content, height=80)
                    edit_url = st.text_input("URL", value=ev.url)
                    edit_screenshot = st.text_input("Screenshot Path", value=ev.screenshot_path)
                    edit_request = st.text_area("HTTP Request", value=ev.request_data, height=80)
                    edit_response = st.text_area("HTTP Response", value=ev.response_data, height=80)
                    if st.form_submit_button("Save Changes", type="primary"):
                        ev_svc.update(
                            ev.id,
                            evidence_type=edit_type,
                            title=edit_title.strip(),
                            content=edit_content.strip(),
                            url=edit_url.strip(),
                            screenshot_path=edit_screenshot.strip(),
                            request_data=edit_request.strip(),
                            response_data=edit_response.strip(),
                        )
                        st.success("Evidence updated.")
                        st.rerun()

            with tab_delete:
                if st.button(f"Delete Evidence #{ev.id}", key=f"del_ev_{ev.id}", type="primary"):
                    ev_svc.delete(ev.id)
                    st.success("Evidence deleted.")
                    st.rerun()
