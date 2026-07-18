"""
Settings — ScopeGuard AI

Application configuration page.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Settings — ScopeGuard AI",
    page_icon="⚙️",
    layout="wide",
)

from database.db import get_db
from services.settings_service import SettingsService
from utilities.helpers import format_datetime

db = get_db()
settings = SettingsService(db)

st.title("⚙️ Settings")
st.caption("Application configuration")
st.divider()

tab_general, tab_db, tab_dirs, tab_integrations, tab_raw = st.tabs(
    ["🎨 General", "🗄️ Database", "📁 Directories", "🔗 Integrations", "🔧 Raw Settings"]
)

# ── General ───────────────────────────────────────────────────────────────────
with tab_general:
    st.subheader("General Settings")
    with st.form("general_settings"):
        app_name = st.text_input(
            "Application Name",
            value=settings.get("app_name", "ScopeGuard AI"),
        )
        theme = st.selectbox(
            "Theme",
            ["dark", "light"],
            index=0 if settings.get("theme", "dark") == "dark" else 1,
        )
        if st.form_submit_button("Save General Settings", type="primary"):
            settings.set("app_name", app_name.strip())
            settings.set("theme", theme)
            st.success("General settings saved.")
            st.rerun()

# ── Database ──────────────────────────────────────────────────────────────────
with tab_db:
    st.subheader("Database Configuration")
    db_path = settings.get("db_path", "data/scopeguard.db")
    st.info(f"Current database path: `{db_path}`")

    with st.form("db_settings"):
        new_db_path = st.text_input("Database Path", value=db_path)
        if st.form_submit_button("Save Database Settings", type="primary"):
            settings.set("db_path", new_db_path.strip())
            st.success("Database settings saved. Restart the app to apply.")

    st.divider()
    st.subheader("Database Stats")
    db_file = Path(db_path)
    if db_file.exists():
        size_kb = db_file.stat().st_size / 1024
        st.metric("Database Size", f"{size_kb:.1f} KB")
        rows = db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        st.write(f"**Tables:** {', '.join(r['name'] for r in rows)}")
    else:
        st.warning("Database file not found at the configured path.")

# ── Directories ───────────────────────────────────────────────────────────────
with tab_dirs:
    st.subheader("Directory Configuration")
    with st.form("dir_settings"):
        reports_dir = st.text_input(
            "Reports Export Directory",
            value=settings.get("reports_dir", "reports/"),
        )
        screenshots_dir = st.text_input(
            "Screenshots Directory",
            value=settings.get("screenshots_dir", "data/screenshots/"),
        )
        if st.form_submit_button("Save Directory Settings", type="primary"):
            settings.set("reports_dir", reports_dir.strip())
            settings.set("screenshots_dir", screenshots_dir.strip())
            st.success("Directory settings saved.")
            st.rerun()

# ── Integrations ──────────────────────────────────────────────────────────────
with tab_integrations:
    st.subheader("GitHub Actions")
    with st.form("gh_settings"):
        gh_enabled = st.checkbox(
            "Enable GitHub Actions integration",
            value=settings.get_bool("github_actions_enabled", False),
        )
        if st.form_submit_button("Save Integration Settings", type="primary"):
            settings.set("github_actions_enabled", "true" if gh_enabled else "false")
            st.success("Integration settings saved.")
            st.rerun()

    st.divider()
    st.info(
        "Future integrations (Jira, Slack, HackerOne API) will appear here in Sprint 3."
    )

# ── Raw Settings ──────────────────────────────────────────────────────────────
with tab_raw:
    st.subheader("All Settings")
    all_settings = settings.list_all()
    for row in all_settings:
        col1, col2, col3 = st.columns([2, 3, 3])
        col1.code(row["key"])
        col2.write(row["value"])
        col3.caption(row.get("description", ""))
