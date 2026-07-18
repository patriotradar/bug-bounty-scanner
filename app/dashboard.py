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
st.subheader("Active research account")

if enabled_accounts:
    selected_account = st.selectbox(
        "Choose the account to use",
        options=enabled_accounts,
        format_func=lambda account: (
            f"{account.get('label', 'Unnamed account')} "
            f"({account.get('email', 'Missing email')})"
        ),
    )

    selected_email = selected_account.get("email", "Missing email")
    selected_id = selected_account.get("id", "missing-id")

    st.success(f"Current account: {selected_email}")
    st.caption(f"Active account ID: {selected_id}")

    if selected_email.endswith("@example.com"):
        st.warning(
            "This still uses a placeholder email. Update "
            "config/approved-accounts.json with your real researcher account."
        )
else:
    selected_account = None
    st.warning(
        "No enabled accounts are available. Enable an authorised account "
        "in config/approved-accounts.json."
    )

st.divider()
st.subheader("Safety check")

account_confirmed = st.checkbox(
    "I confirm that the selected account belongs to me and is authorised "
    "for this programme."
)

if selected_account and account_confirmed:
    st.success("Account safety check passed.")
elif selected_account:
    st.warning(
        "Confirm account ownership before authenticated testing controls "
        "are enabled."
    )

st.divider()
st.subheader("Current workflow")

st.markdown(
    """
    1. Confirm the programme rules and authorised scope.
    2. Add only researcher accounts you created and control.
    3. Select the approved account to use.
    4. Confirm that the account is authorised for the programme.
    5. Run only permitted checks against in-scope targets.
    6. Review findings manually.
    7. Save the smallest necessary evidence.
    8. Generate a report.
    """
)

st.subheader("Authenticated testing status")

if not selected_account:
    st.error("Blocked: no approved research account is enabled.")
elif not account_confirmed:
    st.error("Blocked: account ownership has not been confirmed.")
else:
    st.success(
        "Ready for the next stage. Authenticated controls may use only "
        f"{selected_account.get('email')}."
    )

st.info(
    "The dashboard does not currently log in to any website or store "
    "credentials. Secure credential handling will be added separately."
)