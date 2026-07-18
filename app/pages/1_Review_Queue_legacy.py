from pathlib import Path
import json

import streamlit as st


st.set_page_config(
    page_title="Review Queue",
    page_icon="✅",
    layout="wide",
)

st.title("✅ Action Review Queue")
st.caption("Review proposed verification actions before anything is executed.")

queue_file = Path("data/action-queue.json")


def load_queue():
    if not queue_file.exists():
        return {
            "pending": [],
            "approved": [],
            "rejected": [],
            "completed": [],
        }

    try:
        return json.loads(queue_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        st.error("The action queue could not be loaded.")
        st.stop()


def save_queue(queue):
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    queue_file.write_text(
        json.dumps(queue, indent=2),
        encoding="utf-8",
    )


queue = load_queue()
pending = queue.get("pending", [])

st.warning(
    "Approval does not execute an exploit. It only records that you approved "
    "the proposed minimal verification."
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
            st.write(f"**Asset:** {asset}")
            st.write(f"**Proposed action:** {action}")
            st.write(f"**Purpose:** {purpose}")
            st.write(f"**Maximum requests:** {maximum_requests}")
            st.write(f"**Risk:** {risk}")
            st.caption(f"Proposal ID: {proposal_id}")

            approve_column, reject_column = st.columns(2)

            with approve_column:
                approve = st.button(
                    "Approve",
                    key=f"approve-{proposal_id}",
                    type="primary",
                )

            with reject_column:
                reject = st.button(
                    "Reject",
                    key=f"reject-{proposal_id}",
                )

            if approve:
                approved_proposal = pending.pop(index)
                approved_proposal["status"] = "approved"
                queue.setdefault("approved", []).append(approved_proposal)
                queue["pending"] = pending
                save_queue(queue)
                st.success("Proposal approved and added to the approved queue.")
                st.rerun()

            if reject:
                rejected_proposal = pending.pop(index)
                rejected_proposal["status"] = "rejected"
                queue.setdefault("rejected", []).append(rejected_proposal)
                queue["pending"] = pending
                save_queue(queue)
                st.success("Proposal rejected.")
                st.rerun()

st.divider()

column1, column2, column3, column4 = st.columns(4)

column1.metric("Pending", len(queue.get("pending", [])))
column2.metric("Approved", len(queue.get("approved", [])))
column3.metric("Rejected", len(queue.get("rejected", [])))
column4.metric("Completed", len(queue.get("completed", [])))