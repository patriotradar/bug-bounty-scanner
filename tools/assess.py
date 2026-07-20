#!/usr/bin/env python3
"""
Evidence-driven assessment for ScopeGuard findings.

Given what a URL actually returned (status, headers, body), this decides:
  - what sensitive data (if any) is genuinely present  -> observed_data
  - a severity JUSTIFIED by that evidence (never hard-coded from the template)
  - a confidence level with a reason
  - a descriptive title reflecting what was really found
  - a redacted copy of the body safe to store in a report

Principle: claim only what the evidence supports. A public config file is not
automatically Critical. If the body doesn't prove impact, we downgrade and say so.
"""
import re

# --- secret / sensitive-data detectors -------------------------------------
# Each: (label, compiled regex). Order roughly by seriousness.
DETECTORS = [
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("AWS secret key", re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{30,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b")),
    ("Stripe secret key", re.compile(r"\bsk_live_[0-9A-Za-z]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{30,}\b")),
    ("JWT / access token", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}\b")),
    ("Bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("Database connection string", re.compile(r"(?i)\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|amqp)://[^\s'\"]+")),
    ("Database credentials", re.compile(r"(?i)(?:db_pass(?:word)?|database_password|mysql_pwd)\s*[=:]\s*['\"]?\S+")),
    ("Generic password", re.compile(r"(?i)\b(?:password|passwd|pwd)\s*[=:]\s*['\"]?(?!null|''|\"\")\S{4,}")),
    ("Generic secret / API key", re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]?[A-Za-z0-9._\-]{8,}")),
    ("Cloud storage URL", re.compile(r"(?i)\b(?:[a-z0-9.\-]+\.s3[.\-][a-z0-9.\-]*amazonaws\.com|storage\.googleapis\.com|[a-z0-9.\-]+\.blob\.core\.windows\.net)\S*")),
]

# Non-secret but useful context.
INTERNAL_HOST = re.compile(r"\b(?:(?:10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|[a-z0-9\-]+\.(?:internal|local|corp|intranet)\b)", re.I)
FEATURE_FLAG = re.compile(r"(?i)\b(?:feature[_-]?flag|feature[_-]?toggle|\"?enable[A-Z_])")


def detect_observed(body, headers=None):
    """Return (observed_list, has_real_secret). observed_list is human-readable."""
    body = body or ""
    observed, secret = [], False
    for label, rx in DETECTORS:
        if rx.search(body):
            observed.append(f"{label} (redacted)")
            secret = True
    if INTERNAL_HOST.search(body):
        observed.append("Internal hostname / private IP reference")
    if FEATURE_FLAG.search(body):
        observed.append("Application feature flags / internal settings")
    # de-dup preserve order
    seen, uniq = set(), []
    for o in observed:
        if o not in seen:
            seen.add(o); uniq.append(o)
    if not uniq:
        uniq = ["Public configuration only - no secrets or sensitive data proven in the response"]
    return uniq, secret


def redact(text, limit=4000):
    """Redact secrets from a body so it is safe to paste into a report."""
    if not text:
        return ""
    out = text[:limit]
    for _, rx in DETECTORS:
        out = rx.sub(lambda m: "[REDACTED]", out)
    if len(text) > limit:
        out += f"\n... [truncated, {len(text)} bytes total]"
    return out


def estimate_severity(observed, has_secret, status, body_len, template_sev):
    """Severity justified by evidence, not by the template. Conservative."""
    reachable = status and 200 <= status < 300 and body_len > 0
    if not reachable:
        return ("Informational",
                f"The endpoint returned HTTP {status or 'no response'} with no usable body, so no impact is "
                f"demonstrated. This is a lead to verify manually, not a proven issue.")
    high_value = {"Private key", "AWS secret key", "Stripe secret key", "GitHub token",
                  "Database connection string", "Database credentials", "AWS access key"}
    hit_labels = {o.split(" (")[0] for o in observed}
    if has_secret and hit_labels & high_value:
        return ("High",
                "The response is publicly reachable and contains live-looking credentials or secret material "
                "(see Observed Data). If these are valid production secrets this enables unauthorised access, "
                "so it is treated as High pending confirmation the secrets are active.")
    if has_secret:
        return ("Medium",
                "The response is publicly reachable and exposes token/secret-shaped values (see Observed Data). "
                "Impact depends on whether they are live; rated Medium until verified.")
    if any("Internal hostname" in o or "feature flag" in o.lower() for o in observed):
        return ("Low",
                "The response exposes internal configuration details (hostnames, settings) but no secrets were "
                "proven. Useful for an attacker as reconnaissance; limited direct impact.")
    return ("Low",
            "The file is publicly reachable but the response contains only non-sensitive/public configuration. "
            "No secrets or sensitive data were demonstrated, so impact is limited.")


def confidence_of(status, body_len, has_secret):
    reachable = status and 200 <= status < 300 and body_len > 0
    if not reachable:
        return ("Low", "The endpoint could not be confirmed as returning sensitive content in this capture.")
    if has_secret:
        return ("High", "The exact response was captured and it contains identifiable sensitive patterns.")
    return ("Medium", "The response was captured and is publicly reachable, but no sensitive data was matched, "
                      "so its value needs a human eye.")


def title_for(observed, has_secret, url, fallback):
    """Descriptive, honest title based on what was actually found."""
    path = ""
    m = re.search(r"https?://[^/]+(/\S*)?", url or "")
    if m and m.group(1):
        path = m.group(1)
    labels = {o.split(" (")[0] for o in observed}
    if {"Private key"} & labels:
        return f"Publicly accessible file exposes a private key ({path or url})"
    if {"AWS access key", "AWS secret key", "Stripe secret key", "GitHub token", "Database connection string",
        "Database credentials"} & labels:
        return f"Publicly accessible file exposes production credentials ({path or url})"
    if has_secret:
        return f"Publicly accessible file exposes token/secret-shaped values ({path or url})"
    if any("Internal hostname" in o for o in observed):
        return f"Public file reveals internal configuration and hostnames ({path or url})"
    if observed and observed[0].startswith("Public configuration only"):
        return f"Publicly accessible configuration file - contents appear non-sensitive ({path or url})"
    return fallback or f"Publicly accessible file at {path or url}"


def assess(body, status, headers, url, template_sev="", fallback_title=""):
    observed, has_secret = detect_observed(body, headers)
    body_len = len(body or "")
    severity, justification = estimate_severity(observed, has_secret, status, body_len, template_sev)
    confidence, conf_reason = confidence_of(status, body_len, has_secret)
    title = title_for(observed, has_secret, url, fallback_title)
    return {
        "observed": observed,
        "has_secret": has_secret,
        "severity": severity,
        "severity_justification": justification,
        "confidence": confidence,
        "confidence_reason": conf_reason,
        "title": title,
        "verification_status": "Needs manual review",
        "redacted_body": redact(body),
    }
