from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Bug Bounty Assistant",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Bug Bounty Assistant")
st.caption("Lab-only testing dashboard")

st.warning(
    "Lab mode is enabled. Verification is restricted to approved local test systems."
)

st.subheader("Current system status")

policy_file = Path("policy/verification-rules.json")
allowlist_file = Path("policy/allowed-labs.txt")

col1, col2 = st.columns(2)

with col1:
    if policy_file.exists():
        st.success("Verification policy found")
    else:
        st.error("Verification policy missing")

with col2:
    if allowlist_file.exists():
        st.success("Lab allowlist found")
    else:
        st.error("Lab allowlist missing")

st.subheader("Workflow")

st.markdown(
    """
    1. Add an approved lab target.
    2. Run a Nuclei scan.
    3. Review detected findings.
    4. Approve one controlled verification.
    5. Save minimal evidence.
    6. Generate a report.
    """
)

st.info(
    "The dashboard is working. Scanner and verification controls will be added next."
)