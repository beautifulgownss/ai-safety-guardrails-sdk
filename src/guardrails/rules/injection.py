"""Prompt injection detection rule implementations."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from ..core.guard import BaseRule, RuleContext, RuleResult, Stage

InjectionDetector = Callable[[str], Optional[Tuple[str, str]]]

SUSPICIOUS_PHRASES: Tuple[str, ...] = (
    "ignore previous instructions",
    "disregard earlier guidelines",
    "override safety",
    "pretend to be",
    "you must comply",
    "sudo",
    "root access",
    "reveal your system prompt",
    "developer mode",
)

CODE_BLOCK_PATTERN = re.compile(r"```(?:[\w#+-]+)?\s*[\s\S]*?```", re.IGNORECASE)
SYSTEM_PROMPT_PATTERN = re.compile(r"(system prompt|initial instructions)", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _extract_text(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, Mapping):
        return json.dumps(payload, ensure_ascii=False)
    if isinstance(payload, (list, tuple, set)):
        return " ".join(_extract_text(item) for item in payload)
    return str(payload)


class InjectionRule(BaseRule):
    """Detects potential prompt-injection attempts using multiple strategies."""

    severity = "high"

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        stages: Sequence[Stage] = ("pre", "post"),
        allow_patterns: Optional[Iterable[str]] = None,
        detectors: Optional[Iterable[InjectionDetector]] = None,
        min_findings_to_fail: int = 1,
    ) -> None:
        super().__init__(name=name, stages=stages)
        self.allow_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in allow_patterns or []]
        self.detectors = list(detectors or [])
        self.min_findings_to_fail = max(1, min_findings_to_fail)

    def evaluate(self, payload: Any, context: RuleContext, stage: Stage) -> RuleResult:
        text = _extract_text(payload)
        findings: List[Dict[str, str]] = []

        for pattern in self.allow_patterns:
            if pattern.search(text):
                return RuleResult(
                    rule=self.name,
                    passed=True,
                    stage=stage,
                    severity=self.severity,
                    details={"note": "Content matched allowlist pattern."},
                )

        heuristic_findings = self._heuristic_checks(text)
        findings.extend(heuristic_findings)

        for detector in self.detectors:
            outcome = detector(text)
            if outcome:
                label, explanation = outcome
                findings.append({"type": label, "explanation": explanation})

        passed = len(findings) < self.min_findings_to_fail
        details: Dict[str, Any] = {}
        if findings:
            details["findings"] = findings

        return RuleResult(
            rule=self.name,
            passed=passed,
            stage=stage,
            severity=self.severity,
            details=details,
        )

    def _heuristic_checks(self, text: str) -> List[Dict[str, str]]:
        lowered = text.lower()
        findings: List[Dict[str, str]] = []
        for phrase in SUSPICIOUS_PHRASES:
            if phrase in lowered:
                findings.append(
                    {
                        "type": "suspicious_phrase",
                        "explanation": f"Detected risky instruction: '{phrase}'",
                    }
                )
        if CODE_BLOCK_PATTERN.search(text):
            findings.append(
                {
                    "type": "code_block",
                    "explanation": "Detected embedded code block which may contain override instructions.",
                }
            )
        if SYSTEM_PROMPT_PATTERN.search(text):
            findings.append(
                {
                    "type": "system_prompt_reference",
                    "explanation": "Attempt to reference or leak the system prompt.",
                }
            )
        if URL_PATTERN.search(text):
            findings.append(
                {
                    "type": "external_reference",
                    "explanation": "Contains external URL that may be used for data exfiltration.",
                }
            )
        return findings

