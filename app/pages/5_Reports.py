"""
Reports — ScopeGuard AI

Generate, edit and export vulnerability reports.
Includes HexiStrike report suggestions.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Reports — ScopeGuard AI",
    page_icon="📄",
    layout="wide",
)

from database.db import get_db
from services.finding_service import FindingService
from services.evidence_service import EvidenceService
from services.report_service import ReportService
from hexistrike.report_helper import suggest_report_sections
from utilities.helpers import severity_badge, format_datetime

db = get_db()
find_svc = FindingService(db)
ev_svc = EvidenceService(db)
rpt_svc = ReportService(db)

st.title("📄 Reports")
st.caption("Generate, edit and export vulnerability reports")
st.divider()

tab_list, tab_generate = st.tabs(["📋 All Reports", "✨ Generate Report"])

# ── All Reports ────────────────────────────────────────────────────────────────
with tab_list:
    reports = rpt_svc.list_all()
    if not reports:
        st.info("No reports generated yet. Use the **Generate Report** tab.")
    else:
        st.write(f"**{len(reports)} report(s)**")
        for rpt in reports:
            finding = find_svc.get(rpt.finding_id) if rpt.finding_id else None
            finding_label = (
                f"Finding #{finding.id}: {finding.title}" if finding else "Unlinked"
            )
            with st.expander(f"📄 **{rpt.title}** — {finding_label} · {format_datetime(rpt.created_at)}"):
                tab_view, tab_edit_rpt, tab_export, tab_del = st.tabs(
                    ["📋 View", "✏️ Edit", "📤 Export", "🗑️ Delete"]
                )

                with tab_view:
                    st.markdown(rpt.render_markdown())

                with tab_edit_rpt:
                    with st.form(f"edit_rpt_{rpt.id}"):
                        er_title = st.text_input("Title", value=rpt.title)
                        er_summary = st.text_area("Summary", value=rpt.summary, height=80)
                        er_steps = st.text_area("Steps to Reproduce", value=rpt.steps, height=120)
                        er_expected = st.text_input("Expected Behaviour", value=rpt.expected_behaviour)
                        er_actual = st.text_input("Actual Behaviour", value=rpt.actual_behaviour)
                        er_impact = st.text_area("Impact", value=rpt.impact, height=80)
                        er_evidence = st.text_area("Evidence Summary", value=rpt.evidence_summary, height=80)
                        er_remediation = st.text_area("Suggested Remediation", value=rpt.remediation, height=80)
                        if st.form_submit_button("Save Changes", type="primary"):
                            rpt_svc.update(
                                rpt.id,
                                title=er_title.strip(),
                                summary=er_summary.strip(),
                                steps=er_steps.strip(),
                                expected_behaviour=er_expected.strip(),
                                actual_behaviour=er_actual.strip(),
                                impact=er_impact.strip(),
                                evidence_summary=er_evidence.strip(),
                                remediation=er_remediation.strip(),
                            )
                            st.success("Report saved.")
                            st.rerun()

                with tab_export:
                    st.subheader("Markdown Export")
                    st.download_button(
                        label="⬇️ Download Markdown",
                        data=rpt.render_markdown(),
                        file_name=f"report_{rpt.id}_{rpt.title[:30].replace(' ', '_')}.md",
                        mime="text/markdown",
                    )
                    st.code(rpt.render_markdown(), language="markdown")

                with tab_del:
                    if st.button(f"Delete Report #{rpt.id}", key=f"del_rpt_{rpt.id}", type="primary"):
                        rpt_svc.delete(rpt.id)
                        st.success("Report deleted.")
                        st.rerun()

# ── Generate Report ────────────────────────────────────────────────────────────
with tab_generate:
    st.subheader("✨ Generate a Report from a Finding")

    findings = find_svc.list_all()
    if not findings:
        st.info("No findings yet. Create a finding first.")
        st.stop()

    finding_labels = {f"#{f.id}: {f.title} [{severity_badge(f.severity)}]": f.id for f in findings}
    sel_label = st.selectbox("Select Finding", list(finding_labels.keys()))
    sel_fid = finding_labels[sel_label]
    sel_finding = find_svc.get(sel_fid)

    if sel_finding:
        ev_items = ev_svc.list_for_finding(sel_finding.id)
        suggestions = suggest_report_sections(sel_finding, ev_items)

        st.divider()
        st.write("**🤖 HexiStrike Suggestions** *(edit freely before saving)*")

        with st.form("generate_report"):
            g_title = st.text_input("Title", value=suggestions["title"])
            g_summary = st.text_area("Summary", value=suggestions["summary"], height=80)
            g_steps = st.text_area("Steps to Reproduce", value=suggestions["steps"], height=120)
            g_expected = st.text_input("Expected Behaviour", value=suggestions["expected_behaviour"])
            g_actual = st.text_input("Actual Behaviour", value=suggestions["actual_behaviour"])
            g_impact = st.text_area("Impact", value=suggestions["impact"], height=80)
            g_evidence = st.text_area("Evidence Summary", value=suggestions["evidence_summary"], height=80)
            g_remediation = st.text_area("Suggested Remediation", value=suggestions["remediation"], height=80)

            if st.form_submit_button("Generate & Save Report", type="primary"):
                rpt = rpt_svc.create(
                    finding_id=sel_finding.id,
                    title=g_title.strip(),
                    summary=g_summary.strip(),
                    steps=g_steps.strip(),
                    expected_behaviour=g_expected.strip(),
                    actual_behaviour=g_actual.strip(),
                    impact=g_impact.strip(),
                    evidence_summary=g_evidence.strip(),
                    remediation=g_remediation.strip(),
                )
                st.success(f"✅ Report #{rpt.id} generated successfully.")
                st.balloons()
                st.rerun()
