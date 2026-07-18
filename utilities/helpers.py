"""
General-purpose helper functions used across ScopeGuard AI pages.
"""

from __future__ import annotations

from datetime import datetime

# Emoji badges for severity levels
SEVERITY_BADGES = {
    "critical": "🔴 Critical",
    "high": "🟠 High",
    "medium": "🟡 Medium",
    "low": "🔵 Low",
    "informational": "⚪ Info",
}

# Emoji badges for finding status
STATUS_BADGES = {
    "New": "🆕 New",
    "Investigating": "🔍 Investigating",
    "Needs Evidence": "📷 Needs Evidence",
    "Verified": "✅ Verified",
    "Submitted": "📤 Submitted",
    "Closed": "🔒 Closed",
}


def severity_badge(severity: str) -> str:
    """Return an emoji-prefixed severity label."""
    return SEVERITY_BADGES.get(severity.lower(), severity)


def status_badge(status: str) -> str:
    """Return an emoji-prefixed status label."""
    return STATUS_BADGES.get(status, status)


def truncate(text: str, max_length: int = 80) -> str:
    """Truncate text to max_length characters with an ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def format_datetime(dt_str: str) -> str:
    """Format a SQLite datetime string into a human-readable form."""
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return dt_str
