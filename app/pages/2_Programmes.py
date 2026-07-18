"""
Programme Manager — ScopeGuard AI

Create, edit, delete, enable, disable and search bug bounty programmes.
Manage in-scope assets per programme.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Programmes — ScopeGuard AI",
    page_icon="🎯",
    layout="wide",
)

from database.db import get_db
from services.programme_service import ProgrammeService
from models.asset import ASSET_TYPES
from utilities.helpers import format_datetime

db = get_db()
svc = ProgrammeService(db)

st.title("🎯 Programme Manager")
st.caption("Manage your authorised bug bounty programmes and their assets")
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
if "selected_programme_id" not in st.session_state:
    st.session_state.selected_programme_id = None

# ── Sidebar: create / search ──────────────────────────────────────────────────
with st.sidebar:
    st.subheader("🔎 Search")
    search_query = st.text_input("Search programmes", placeholder="Name, platform…")
    st.divider()
    st.subheader("➕ New Programme")
    with st.form("new_programme_form", clear_on_submit=True):
        new_name = st.text_input("Name *", placeholder="HackerOne Programme")
        new_platform = st.text_input("Platform", placeholder="HackerOne / Bugcrowd")
        new_notes = st.text_area("Notes", height=80)
        new_scope = st.text_area("Scope Summary", height=80)
        new_enabled = st.checkbox("Enabled", value=True)
        submitted = st.form_submit_button("Create Programme", type="primary")
        if submitted:
            if not new_name.strip():
                st.error("Programme name is required.")
            else:
                prog = svc.create(
                    name=new_name.strip(),
                    platform=new_platform.strip(),
                    enabled=new_enabled,
                    notes=new_notes.strip(),
                    scope_summary=new_scope.strip(),
                )
                st.success(f"Programme '{prog.name}' created.")
                st.session_state.selected_programme_id = prog.id
                st.rerun()

# ── Programme list ────────────────────────────────────────────────────────────
if search_query:
    programmes = svc.search(search_query)
else:
    programmes = svc.list_all()

if not programmes:
    st.info("No programmes found. Use the sidebar to create your first programme.")
    st.stop()

# ── Summary metrics ────────────────────────────────────────────────────────────
total = len(programmes)
active = sum(1 for p in programmes if p.enabled)
col1, col2, col3 = st.columns(3)
col1.metric("Total Programmes", total)
col2.metric("Active", active)
col3.metric("Disabled", total - active)
st.divider()

# ── Programme cards ────────────────────────────────────────────────────────────
for prog in programmes:
    status_icon = "🟢" if prog.enabled else "🔴"
    assets = svc.list_assets(prog.id)

    with st.expander(
        f"{status_icon} **{prog.name}** — {prog.platform or 'No platform'} "
        f"({len(assets)} assets)",
        expanded=(st.session_state.selected_programme_id == prog.id),
    ):
        tab_details, tab_assets, tab_edit, tab_danger = st.tabs(
            ["📋 Details", "🌐 Assets", "✏️ Edit", "🗑️ Danger"]
        )

        # ── Details ──────────────────────────────────────────────────────────
        with tab_details:
            col1, col2 = st.columns(2)
            col1.write(f"**ID:** `{prog.id}`")
            col2.write(f"**Platform:** {prog.platform or '—'}")
            col1.write(f"**Status:** {'✅ Enabled' if prog.enabled else '❌ Disabled'}")
            col2.write(f"**Created:** {format_datetime(prog.created_at)}")
            if prog.notes:
                st.write("**Notes:**")
                st.write(prog.notes)
            if prog.scope_summary:
                st.write("**Scope Summary:**")
                st.write(prog.scope_summary)
            c1, c2 = st.columns(2)
            with c1:
                if prog.enabled:
                    if st.button("Disable", key=f"disable_{prog.id}"):
                        svc.disable(prog.id)
                        st.success(f"'{prog.name}' disabled.")
                        st.rerun()
                else:
                    if st.button("Enable", key=f"enable_{prog.id}", type="primary"):
                        svc.enable(prog.id)
                        st.success(f"'{prog.name}' enabled.")
                        st.rerun()

        # ── Assets ────────────────────────────────────────────────────────────
        with tab_assets:
            st.write(f"**{len(assets)} in-scope asset(s)**")

            # Add asset form
            with st.form(f"add_asset_{prog.id}", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                asset_type = c1.selectbox("Type", ASSET_TYPES, key=f"atype_{prog.id}")
                asset_value = c2.text_input("Value", placeholder="example.com", key=f"aval_{prog.id}")
                asset_wc = c3.checkbox("Wildcard", key=f"awc_{prog.id}")
                asset_notes = st.text_input("Notes", key=f"anotes_{prog.id}")
                if st.form_submit_button("Add Asset"):
                    if asset_value.strip():
                        svc.add_asset(
                            programme_id=prog.id,
                            asset_type=asset_type,
                            value=asset_value.strip(),
                            wildcard=asset_wc,
                            notes=asset_notes.strip(),
                        )
                        st.success(f"Asset '{asset_value}' added.")
                        st.rerun()
                    else:
                        st.error("Asset value is required.")

            if assets:
                for asset in assets:
                    ac1, ac2, ac3, ac4, ac5 = st.columns([1, 3, 1, 2, 1])
                    ac1.caption(asset.asset_type)
                    ac2.code(asset.value)
                    ac3.write("🌐" if asset.wildcard else "")
                    ac4.caption(asset.notes or "—")
                    if ac5.button("🗑️", key=f"del_asset_{asset.id}", help="Delete asset"):
                        svc.delete_asset(asset.id)
                        st.success("Asset deleted.")
                        st.rerun()
            else:
                st.info("No assets configured for this programme yet.")

        # ── Edit ──────────────────────────────────────────────────────────────
        with tab_edit:
            with st.form(f"edit_prog_{prog.id}"):
                edit_name = st.text_input("Name", value=prog.name)
                edit_platform = st.text_input("Platform", value=prog.platform)
                edit_notes = st.text_area("Notes", value=prog.notes, height=80)
                edit_scope = st.text_area("Scope Summary", value=prog.scope_summary, height=80)
                if st.form_submit_button("Save Changes", type="primary"):
                    if not edit_name.strip():
                        st.error("Name is required.")
                    else:
                        svc.update(
                            prog.id,
                            name=edit_name.strip(),
                            platform=edit_platform.strip(),
                            notes=edit_notes.strip(),
                            scope_summary=edit_scope.strip(),
                        )
                        st.success("Programme updated.")
                        st.rerun()

        # ── Danger Zone ───────────────────────────────────────────────────────
        with tab_danger:
            st.warning(
                "Deleting a programme is permanent and also removes all linked assets."
            )
            confirm = st.text_input(
                f"Type **{prog.name}** to confirm deletion",
                key=f"confirm_del_{prog.id}",
            )
            if st.button("Delete Programme", type="primary", key=f"del_prog_{prog.id}"):
                if confirm.strip() == prog.name:
                    svc.delete(prog.id)
                    st.success(f"Programme '{prog.name}' deleted.")
                    if st.session_state.selected_programme_id == prog.id:
                        st.session_state.selected_programme_id = None
                    st.rerun()
                else:
                    st.error("Programme name does not match. Deletion cancelled.")
