"""
Review Queue — ScopeGuard AI

Review proposed verification actions before anything is executed.
Preserves the original human-approval workflow while integrating with the DB.
"""

import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Review Queue — ScopeGuard AI",
    page_icon="✅",
    layout="wide",
)

from database.db import get_db
from history.logger import log

db = get_db()

st.title("✅ Action Review Queue")
st.caption(
    "Review proposed verification actions before anything is executed. "
    "Approval records your decision — it does not execute any exploit."
)
st.divider()

# ── Load queue from JSON (preserved from original implementation) ─────────────
queue_file = Path("data/action-queue.json")


def load_queue():
    if not queue_file.exists():
        return {"pending": [], "approved": [], "rejected": [], "completed": []}
    try:
        return json.loads(queue_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        st.error("The action queue could not be loaded.")
        st.stop()


def save_queue(queue: dict) -> None:
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    queue_file.write_text(json.dumps(queue, indent=2), encoding="utf-8")


queue = load_queue()
pending = queue.get("pending", [])

st.warning(
    "⚠️ Approval does **not** execute an exploit. It only records that you "
    "approved the proposed minimal verification step."
)

if not pending:
    st.info("There are currently no verification proposals waiting for review.")
else:
    for index, proposal in enumerate(pending):
        proposal_id = proposal.get("id", f"proposal-{index + 1}")
        finding_type = proposal.get("finding_type", "Unknown finding")
        asset = proposal.get("asset", "Unknown asset")
        action = proposal.get("action", "No action supplied")
        purpose = proposal.get("purpose", "No purpose supplied")
        maximum_requests = proposal.get("maximum_requests", 1)
        risk = proposal.get("risk", "Not assessed")

        with st.container(border=True):
            st.subheader(finding_type)
            col1, col2 = st.columns(2)
            col1.write(f"**Asset:** {asset}")
            col2.write(f"**Risk:** {risk}")
            col1.write(f"**Proposed action:** {action}")
            col2.write(f"**Maximum requests:** {maximum_requests}")
            st.write(f"**Purpose:** {purpose}")
            st.caption(f"Proposal ID: {proposal_id}")

            approve_col, reject_col = st.columns(2)

            with approve_col:
                approve = st.button(
                    "✅ Approve",
                    key=f"approve-{proposal_id}",
                    type="primary",
                )

            with reject_col:
                reject = st.button(
                    "❌ Reject",
                    key=f"reject-{proposal_id}",
                )

            if approve:
                approved_proposal = pending.pop(index)
                approved_proposal["status"] = "approved"
                queue.setdefault("approved", []).append(approved_proposal)
                queue["pending"] = pending
                save_queue(queue)
                log(
                    event_type="proposal_approved",
                    entity_type="proposal",
                    entity_id=proposal_id,
                    description=f"Proposal approved: {finding_type} on {asset}",
                    db=db,
                )
                st.success("Proposal approved and added to the approved queue.")
                st.rerun()

            if reject:
                rejected_proposal = pending.pop(index)
                rejected_proposal["status"] = "rejected"
                queue.setdefault("rejected", []).append(rejected_proposal)
                queue["pending"] = pending
                save_queue(queue)
                log(
                    event_type="proposal_rejected",
                    entity_type="proposal",
                    entity_id=proposal_id,
                    description=f"Proposal rejected: {finding_type} on {asset}",
                    db=db,
                )
                st.success("Proposal rejected.")
                st.rerun()

st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pending", len(queue.get("pending", [])))
col2.metric("Approved", len(queue.get("approved", [])))
col3.metric("Rejected", len(queue.get("rejected", [])))
col4.metric("Completed", len(queue.get("completed", [])))
