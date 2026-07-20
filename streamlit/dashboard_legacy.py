from pathlib import Path
import json

import streamlit as st


st.set_page_config(
    page_title="Bug Bounty Assistant",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Bug Bounty Assistant")
st.caption("Authorised bug bounty testing dashboard")

st.warning(
    "Only test accounts, applications and targets that are explicitly "
    "included in the programme rules and scope."
)

policy_file = Path("policy/verification-rules.json")
allowlist_file = Path("policy/allowed-labs.txt")
accounts_file = Path("config/approved-accounts.json")
programmes_file = Path("config/programmes.json")


def load_json_file(path: Path, description: str) -> dict:
    """Load a JSON configuration file or stop the dashboard safely."""

    if not path.exists():
        st.error(f"{description} is missing: {path}")
        st.stop()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        st.error(f"{description} contains invalid JSON: {exc}")
        st.stop()
    except OSError as exc:
        st.error(f"Could not read {description}: {exc}")
        st.stop()

    if not isinstance(data, dict):
        st.error(f"{description} must contain a JSON object.")
        st.stop()

    return data


st.subheader("System status")

status_columns = st.columns(4)

status_files = [
    ("Verification policy", policy_file),
    ("Target allowlist", allowlist_file),
    ("Approved accounts", accounts_file),
    ("Programme configuration", programmes_file),
]

for column, (label, path) in zip(status_columns, status_files):
    with column:
        if path.exists():
            st.success(f"{label} found")
        else:
            st.error(f"{label} missing")


account_data = load_json_file(
    accounts_file,
    "Approved accounts configuration",
)

programme_data = load_json_file(
    programmes_file,
    "Programme configuration",
)

accounts = account_data.get("accounts", [])
programmes = programme_data.get("programmes", [])

if not isinstance(accounts, list):
    st.error("The accounts field must be a list.")
    st.stop()

if not isinstance(programmes, list):
    st.error("The programmes field must be a list.")
    st.stop()

enabled_programmes = [
    programme
    for programme in programmes
    if programme.get("enabled") is True
]

if not enabled_programmes:
    st.error("No bug bounty programmes are enabled.")
    st.stop()

st.divider()
st.subheader("Programme")

selected_programme = st.selectbox(
    "Choose the authorised programme",
    options=enabled_programmes,
    format_func=lambda programme: programme.get(
        "name",
        programme.get("id", "Unnamed programme"),
    ),
)

programme_id = selected_programme.get("id", "")
programme_name = selected_programme.get(
    "name",
    programme_id or "Unnamed programme",
)

programme_rules = selected_programme.get("rules", {})
programme_assets = selected_programme.get("assets", [])
account_required = selected_programme.get(
    "account_required",
    False,
)

if not isinstance(programme_rules, dict):
    st.error("The selected programme rules must be a JSON object.")
    st.stop()

if not isinstance(programme_assets, list):
    st.error("The selected programme assets must be a list.")
    st.stop()

st.success(f"Selected programme: {programme_name}")

st.divider()
st.subheader("Programme rules")

rule_col1, rule_col2, rule_col3 = st.columns(3)

automated_scanning = programme_rules.get(
    "automated_scanning",
    False,
)

authenticated_testing = programme_rules.get(
    "authenticated_testing",
    False,
)

multiple_test_accounts = programme_rules.get(
    "multiple_test_accounts",
    False,
)

with rule_col1:
    if automated_scanning:
        st.success("Automated scanning permitted")
    else:
        st.error("Automated scanning not approved")

with rule_col2:
    if authenticated_testing:
        st.success("Authenticated testing permitted")
    else:
        st.error("Authenticated testing not approved")

with rule_col3:
    if multiple_test_accounts:
        st.success("Multiple test accounts permitted")
    else:
        st.warning("Multiple test accounts not confirmed")

rate_limit_notes = programme_rules.get(
    "rate_limit_notes",
    "",
)

if rate_limit_notes:
    st.info(f"Rate-limit notes: {rate_limit_notes}")
else:
    st.warning(
        "No rate-limit information has been recorded. "
        "Do not run automated requests until the programme rules are confirmed."
    )

prohibited_tests = programme_rules.get(
    "prohibited_tests",
    [],
)

if prohibited_tests:
    st.write("**Prohibited testing:**")

    for prohibited_test in prohibited_tests:
        st.write(f"- {prohibited_test}")
else:
    st.warning(
        "No prohibited-test list has been recorded yet. "
        "This does not mean every test is permitted."
    )

st.divider()
st.subheader("In-scope assets")

if programme_assets:
    for asset in programme_assets:
        if isinstance(asset, str):
            st.code(asset)
        elif isinstance(asset, dict):
            asset_value = asset.get(
                "value",
                asset.get("url", asset.get("host", "Missing asset")),
            )
            asset_type = asset.get("type", "unspecified")
            st.write(f"**{asset_value}**")
            st.caption(f"Asset type: {asset_type}")
else:
    st.error(
        "No assets have been added to this programme. "
        "Scanning and authenticated testing must remain blocked."
    )

st.divider()
st.subheader("Approved researcher accounts")

enabled_accounts = [
    account
    for account in accounts
    if account.get("enabled") is True
]

programme_accounts = [
    account
    for account in enabled_accounts
    if programme_id in account.get("approved_programmes", [])
]

if not enabled_accounts:
    st.warning("No researcher accounts are currently enabled.")
else:
    for account in enabled_accounts:
        email = account.get("email", "Missing email")
        label = account.get("label", "Unnamed account")
        account_id = account.get("id", "missing-id")
        approved_programmes = account.get(
            "approved_programmes",
            [],
        )

        with st.container(border=True):
            st.write(f"**{label}**")
            st.write(email)
            st.caption(f"Account ID: {account_id}")

            if programme_id in approved_programmes:
                st.success("Approved for the selected programme")
            else:
                st.error("Not approved for the selected programme")

st.info(
    "Do not place passwords, session cookies, API tokens, recovery codes "
    "or other credentials inside approved-accounts.json."
)

st.divider()
st.subheader("Active research account")

if not account_required:
    selected_account = None
    st.info(
        "The selected programme does not currently require an account."
    )
elif not authenticated_testing:
    selected_account = None
    st.error(
        "Authenticated account use is blocked because authenticated testing "
        "is not approved in the programme configuration."
    )
elif programme_accounts:
    selected_account = st.selectbox(
        "Choose the account to use",
        options=programme_accounts,
        format_func=lambda account: (
            f"{account.get('label', 'Unnamed account')} "
            f"({account.get('email', 'Missing email')})"
        ),
    )

    selected_email = selected_account.get(
        "email",
        "Missing email",
    )
    selected_id = selected_account.get(
        "id",
        "missing-id",
    )

    st.success(f"Current account: {selected_email}")
    st.caption(f"Active account ID: {selected_id}")

    if selected_email.endswith("@example.com"):
        st.warning(
            "This account still uses a placeholder email address."
        )
else:
    selected_account = None
    st.error(
        "No enabled account is approved for this programme."
    )

if (
    len(programme_accounts) > 1
    and not multiple_test_accounts
):
    st.error(
        "More than one account is enabled for this programme, but multiple "
        "test accounts have not been confirmed as permitted."
    )

st.divider()
st.subheader("Safety confirmation")

account_confirmed = st.checkbox(
    "I confirm that the selected account belongs to me and is authorised "
    "for this programme.",
    disabled=selected_account is None,
)

scope_confirmed = st.checkbox(
    "I confirm that I have checked the current programme scope and rules."
)

st.divider()
st.subheader("Testing status")

blocking_reasons = []

if not programme_assets:
    blocking_reasons.append(
        "No in-scope assets are configured."
    )

if account_required:
    if not authenticated_testing:
        blocking_reasons.append(
            "Authenticated testing is not approved."
        )

    if selected_account is None:
        blocking_reasons.append(
            "No approved research account is selected."
        )

    if selected_account and not account_confirmed:
        blocking_reasons.append(
            "Account ownership has not been confirmed."
        )

if len(programme_accounts) > 1 and not multiple_test_accounts:
    blocking_reasons.append(
        "Multiple accounts are enabled without programme approval."
    )

if not scope_confirmed:
    blocking_reasons.append(
        "The current scope and rules have not been confirmed."
    )

if blocking_reasons:
    st.error("Testing controls remain blocked.")

    for reason in blocking_reasons:
        st.write(f"- {reason}")
else:
    st.success(
        "The programme, scope and account safety checks have passed."
    )

    if not automated_scanning:
        st.warning(
            "Automated scanning remains disabled by the programme rules."
        )

st.divider()
st.subheader("Current workflow")

st.markdown(
    """
    1. Select the authorised bug bounty programme.
    2. Review the programme rules and prohibited tests.
    3. Confirm the exact in-scope assets.
    4. Select only an account approved for that programme.
    5. Confirm account ownership and scope authorisation.
    6. Run only the testing methods explicitly permitted.
    7. Review evidence manually.
    8. Generate a clear, reproducible report.
    """
)

st.info(
    "The dashboard does not yet log in, store credentials or send "
    "authenticated requests."
)