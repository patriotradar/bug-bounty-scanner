"""
HexiStrike Report Helper — assists drafting vulnerability reports.

Generates structured report section suggestions based on finding data.
Does not write or submit reports automatically.
"""

from __future__ import annotations

from typing import Dict, List

from models.finding import Finding
from models.evidence import Evidence


# Impact templates keyed on severity
IMPACT_TEMPLATES = {
    "critical": (
        "This vulnerability has critical severity and could allow an attacker "
        "to fully compromise the affected system, exfiltrate sensitive data, "
        "or cause significant harm to users. Immediate remediation is required."
    ),
    "high": (
        "This high severity vulnerability could allow an attacker to access "
        "sensitive data, bypass authentication controls, or significantly "
        "impact the confidentiality, integrity, or availability of the system."
    ),
    "medium": (
        "This medium severity vulnerability may allow an attacker to gain "
        "limited unauthorised access or disclose non-critical information. "
        "Prompt remediation is recommended."
    ),
    "low": (
        "This low severity issue presents a minor security risk. While limited "
        "in immediate impact, it should be addressed to reduce attack surface."
    ),
    "informational": (
        "This is an informational finding that does not directly represent a "
        "vulnerability but highlights a configuration or design consideration "
        "worth reviewing."
    ),
}

# Remediation templates keyed on common finding keywords
REMEDIATION_KEYWORDS: List[tuple] = [
    (["xss", "cross-site scripting", "script injection"],
     "Encode all user-supplied output using context-appropriate escaping "
     "(HTML, JavaScript, CSS). Implement a strong Content Security Policy (CSP)."),
    (["sql", "injection", "sqli"],
     "Use parameterised queries or prepared statements. Never concatenate "
     "user input directly into SQL. Apply least-privilege database accounts."),
    (["idor", "insecure direct object", "authorisation"],
     "Enforce server-side authorisation checks for every object access. "
     "Use indirect references (UUIDs or tokens) rather than sequential IDs."),
    (["open redirect", "redirect"],
     "Validate redirect destinations against an allowlist of trusted URLs. "
     "Never include user-controlled input in redirect targets without validation."),
    (["csrf", "cross-site request forgery"],
     "Implement anti-CSRF tokens on all state-changing requests. "
     "Consider SameSite cookie attributes."),
    (["ssrf", "server-side request"],
     "Validate and restrict outbound request URLs to an allowlist. "
     "Block requests to internal IP ranges."),
    (["path traversal", "directory traversal"],
     "Canonicalise file paths and verify they remain within the intended base "
     "directory before any file operation."),
    (["xxe", "xml external entity"],
     "Disable external entity processing in the XML parser configuration."),
    (["rce", "remote code execution", "command injection"],
     "Never pass user-supplied data to shell commands. Use language-native "
     "APIs instead of system calls."),
]


def _match_remediation(title: str, description: str) -> str:
    """Return a remediation template that matches the finding text, or a generic fallback."""
    combined = f"{title} {description}".lower()
    for keywords, template in REMEDIATION_KEYWORDS:
        if any(kw in combined for kw in keywords):
            return template
    return (
        "Review the affected component and apply the principle of least privilege. "
        "Consult the OWASP guidelines relevant to this vulnerability class."
    )


def suggest_report_sections(
    finding: Finding, evidence: List[Evidence]
) -> Dict[str, str]:
    """
    Return a dictionary of suggested report section content.

    Keys: title, summary, steps, expected_behaviour, actual_behaviour,
          impact, evidence_summary, remediation
    """
    # Build evidence summary
    ev_lines: List[str] = []
    for ev in evidence:
        label = ev.title or ev.evidence_type
        if ev.url:
            ev_lines.append(f"- **{label}**: {ev.url}")
        elif ev.content:
            snippet = ev.content[:200].replace("\n", " ")
            ev_lines.append(f"- **{label}**: {snippet}")
        else:
            ev_lines.append(f"- {label} (no content recorded)")
    evidence_summary = "\n".join(ev_lines) if ev_lines else "_No evidence attached yet._"

    # Steps to reproduce placeholder
    steps = (
        "1. Log in to the application as a low-privileged user.\n"
        "2. Navigate to the affected endpoint: `{asset}`.\n"
        "3. Submit the following payload: [describe payload].\n"
        "4. Observe the response confirming the vulnerability."
    ).format(asset=finding.asset or "<asset>")

    return {
        "title": f"{finding.title} — {finding.severity.capitalize()} Severity",
        "summary": (
            finding.description
            or f"A {finding.severity} severity vulnerability was identified on "
               f"{finding.asset or 'the target'}."
        ),
        "steps": steps,
        "expected_behaviour": (
            "The application should validate and sanitise input, "
            "enforcing appropriate security controls on this endpoint."
        ),
        "actual_behaviour": (
            finding.description
            or "The application responded in an unexpected or insecure manner, "
               "confirming the presence of the vulnerability."
        ),
        "impact": IMPACT_TEMPLATES.get(
            finding.severity.lower(),
            IMPACT_TEMPLATES["medium"],
        ),
        "evidence_summary": evidence_summary,
        "remediation": _match_remediation(finding.title, finding.description),
    }
