"""
Activity History — ScopeGuard AI

Displays the immutable audit log of all platform events.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Activity History — ScopeGuard AI",
    page_icon="📜",
    layout="wide",
)

from database.db import get_db
from services.activity_service import ActivityService
from utilities.helpers import format_datetime

db = get_db()
act_svc = ActivityService(db)

st.title("📜 Activity History")
st.caption("Immutable audit log of all platform events — newest first")
st.divider()

# ── Metrics ───────────────────────────────────────────────────────────────────
total_events = act_svc.count()
col1, col2 = st.columns(2)
col1.metric("Total Events", total_events)

# ── Filters ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Filter")
    limit = st.slider("Show last N events", min_value=10, max_value=500, value=50, step=10)
    filter_type = st.text_input("Event type filter", placeholder="finding_created…")

# ── Event list ────────────────────────────────────────────────────────────────
events = act_svc.list_recent(limit=limit)

if filter_type.strip():
    events = [e for e in events if filter_type.strip().lower() in e.event_type.lower()]

if not events:
    st.info("No activity recorded yet.")
    st.stop()

st.write(f"**Showing {len(events)} event(s)**")

ICON_MAP = {
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

for event in events:
    icon = ICON_MAP.get(event.event_type, "📌")
    col1, col2, col3, col4 = st.columns([1, 2, 5, 2])
    col1.write(icon)
    col2.caption(event.event_type)
    col3.write(event.description)
    col4.caption(format_datetime(event.created_at))
