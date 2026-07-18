from pathlib import Path
import json

import streamlit as st


st.set_page_config(
    page_title="Bug Bounty Assistant",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Bug Bounty Assistant")
st.caption("Authorised testing dashboard")

st.warning(
    "Only use accounts and targets you own or are explicitly authorised to test."
)

policy_file = Path("policy/verification-rules.json")
allowlist_file = Path("policy/allowed-labs.txt")
accounts_file = Path("config/approved-accounts.json")

st.subheader("System status")

col1, col2, col3 = st.columns(3)

with col1:
    if policy_file.exists():
        st.success("Verification policy found")
    else:
        st.error("Verification policy missing")

with col2:
    if allowlist_file.exists():
        st.success("Target allowlist found")
    else:
        st.error("Target allowlist missing")

with col3:
    if accounts_file.exists():
        st.success("Approved accounts file found")
    else:
        st.error("Approved accounts file missing")

st.divider()
st.subheader("Approved researcher accounts")

if not accounts_file.exists():
    st.error("Create config/approved-accounts.json before continuing.")
    st.stop()

try:
    account_data = json.loads(accounts_file.read_text(encoding="utf-8"))
    accounts = account_data.get("accounts", [])
except (json.JSONDecodeError, OSError) as exc:
    st.error(f"Could not read approved accounts: {exc}")
    st.stop()

enabled_accounts = [
    account
    for account in accounts
    if account.get("enabled") is True
]

if not enabled_accounts:
    st.warning("No researcher accounts are currently enabled.")
else:
    for account in enabled_accounts:
        email = account.get("email", "Missing email")
        label = account.get("label", "Unnamed account")
        account_id = account.get("id", "missing-id")

        with st.container(border=True):
            st.write(f"**{label}**")
            st.write(email)
            st.caption(f"Account ID: {account_id}")
            st.success("Approved and enabled")

st.info(
    "Passwords, session cookies and API tokens must not be stored in "
    "approved-accounts.json."
)

st.divider()
st.subheader("Workflow")

st.markdown(
    """
    1. Confirm the programme rules and authorised scope.
    2. Add only your researcher accounts.
    3. Select an approved account.
    4. Run permitted checks.
    5. Review findings manually.
    6. Save minimal evidence.
    7. Generate a report.
    """
)