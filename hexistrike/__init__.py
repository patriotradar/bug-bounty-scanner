"""
HexiStrike — Sprint 2 analysis module for ScopeGuard AI.

This module provides analytical assistance for a human security researcher.
It NEVER executes attacks, sends requests, or performs any offensive actions.
All output is advisory only.
"""

from hexistrike.analysis import analyse_finding, detect_duplicates
from hexistrike.prioritiser import prioritise_findings
from hexistrike.report_helper import suggest_report_sections

__all__ = [
    "analyse_finding",
    "detect_duplicates",
    "prioritise_findings",
    "suggest_report_sections",
]
