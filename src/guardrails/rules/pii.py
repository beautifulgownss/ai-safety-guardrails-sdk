"""PII detection rule for the AI Safety Guardrails SDK."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set

from ..core.guard import BaseRule, GuardConfigurationError, RuleContext, RuleResult, Stage

# Common PII regex patterns. These are intentionally strict to reduce false positives.
DEFAULT_PATTERNS: Mapping[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE),
    "phone": re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}",
    ),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(
        r"\b(?:\d[ -]*?){13,16}\b",
    ),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),
}


def _flatten_payload(payload: Any) -> Iterable[str]:
    """Yield string fragments from arbitrary data structures."""
    if payload is None:
        return []
    if isinstance(payload, str):
        return [payload]
    if isinstance(payload, Mapping):
        return [json.dumps(payload, ensure_ascii=False)]
    if isinstance(payload, Sequence) and not isinstance(payload, (bytes, bytearray)):
        fragments: List[str] = []
        for item in payload:
            fragments.extend(_flatten_payload(item))
        return fragments
    return [str(payload)]


class PIIRule(BaseRule):
    """Detects common personal identifiable information in responses."""

    severity = "critical"

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        stages: Sequence[Stage] = ("post",),
        patterns: Optional[Mapping[str, re.Pattern[str]]] = None,
        allowlist: Optional[Iterable[str]] = None,
        match_limit: int = 20,
    ) -> None:
        super().__init__(name=name, stages=stages)
        self.patterns: Mapping[str, re.Pattern[str]] = patterns or DEFAULT_PATTERNS
        if not self.patterns:
            raise GuardConfigurationError("PIIRule requires at least one detection pattern.")
        self.allowlist: Set[str] = {item.lower() for item in allowlist or []}
        self.match_limit = match_limit

    def evaluate(self, payload: Any, context: RuleContext, stage: Stage) -> RuleResult:
        matches: MutableMapping[str, List[str]] = {}
        for fragment in _flatten_payload(payload):
            if not fragment:
                continue
            lowered_fragment = fragment.lower()
            for entity, pattern in self.patterns.items():
                if entity in matches and len(matches[entity]) >= self.match_limit:
                    continue
                found = pattern.findall(fragment)
                filtered = [
                    match
                    for match in found
                    if match and match.lower() not in self.allowlist
                ]
                if filtered:
                    entity_matches = matches.setdefault(entity, [])
                    entity_matches.extend(filtered[: self.match_limit - len(entity_matches)])
        passed = not matches
        details: Dict[str, Any] = {}
        if matches:
            details["matches"] = {key: list(set(value)) for key, value in matches.items()}
        return RuleResult(
            rule=self.name,
            passed=passed,
            stage=stage,
            severity=self.severity,
            details=details,
        )

