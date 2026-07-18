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
st.subheader("Programme")

programme_options = ["trip"]

selected_programme = st.selectbox(
    "Choose the bug bounty programme",
    options=programme_options,
    format_func=lambda value: value.title(),
)

st.success(f"Selected programme: {selected_programme.title()}")

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

programme_accounts = [
    account
    for account in enabled_accounts
    if selected_programme in account.get("approved_programmes", [])
]

if not enabled_accounts:
    st.warning("No researcher accounts are currently enabled.")
else:
    for account in enabled_accounts:
        email = account.get("email", "Missing email")
        label = account.get("label", "Unnamed account")
        account_id = account.get("id", "missing-id")
        approved_programmes = account.get("approved_programmes", [])

        with st.container(border=True):
            st.write(f"**{label}**")
            st.write(email)
            st.caption(f"Account ID: {account_id}")
            st.caption(
                "Approved programmes: "
                + (
                    ", ".join(approved_programmes)
                    if approved_programmes
                    else "None"
                )
            )

            if selected_programme in approved_programmes:
                st.success("Approved for the selected programme")
            else:
                st.error("Not approved for the selected programme")

st.info(
    "Passwords, session cookies and API tokens must not be stored in "
    "approved-accounts.json."
)

st.divider()
st.subheader("Active research account")

if programme_accounts:
    selected_account = st.selectbox(
        "Choose the account to use",
        options=programme_accounts,
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
    st.error(
        "No enabled account is approved for the selected programme."
    )

st.divider()
st.subheader("Safety check")

account_confirmed = st.checkbox(
    "I confirm that the selected account belongs to me and is authorised "
    "for the selected programme."
)

if selected_account and account_confirmed:
    st.success("Account safety check passed.")
elif selected_account:
    st.warning(
        "Confirm account ownership before authenticated testing controls "
        "are enabled."
    )

st.divider()
st.subheader("Authenticated testing status")

if not selected_account:
    st.error(
        "Blocked: no approved account is available for this programme."
    )
elif selected_programme not in selected_account.get(
    "approved_programmes", []
):
    st.error(
        "Blocked: the selected account is not approved for this programme."
    )
elif not account_confirmed:
    st.error("Blocked: account ownership has not been confirmed.")
else:
    st.success(
        "Ready for the next stage. Authenticated controls may use only "
        f"{selected_account.get('email')} for "
        f"{selected_programme.title()}."
    )

st.divider()
st.subheader("Current workflow")

st.markdown(
    """
    1. Select the authorised bug bounty programme.
    2. Load only accounts explicitly approved for that programme.
    3. Select the account you created and control.
    4. Confirm ownership and authorisation.
    5. Run only permitted checks against in-scope targets.
    6. Review findings manually.
    7. Save the smallest necessary evidence.
    8. Generate a report.
    """
)

st.info(
    "The dashboard still does not log in to any website, store credentials "
    "or send authenticated requests."
)