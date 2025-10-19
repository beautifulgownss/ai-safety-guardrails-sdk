"""Unit tests for the Guard class and bundled rules."""

import pytest
from pydantic import BaseModel

from guardrails import (
    Guard,
    GuardViolation,
    InjectionRule,
    PIIRule,
    RuleContext,
    SchemaRule,
)


class MessageSchema(BaseModel):
    message: str
    channel: str


def test_guard_allows_clean_output():
    guard = Guard(rules=[InjectionRule(), PIIRule(), SchemaRule(MessageSchema)])

    @guard.protect
    def safe_response() -> dict:
        return {"message": "All systems operational.", "channel": "web"}

    assert safe_response()["message"] == "All systems operational."


def test_guard_blocks_pii_detection():
    guard = Guard(rules=[PIIRule()])

    @guard.protect
    def unsafe_response() -> str:
        return "Call me at 555-1234 for details."

    with pytest.raises(GuardViolation):
        unsafe_response()


def test_manual_check_reports_failures():
    guard = Guard(rules=[SchemaRule(MessageSchema)])
    context = RuleContext(inputs={}, metadata={})
    report = guard.check({"message": "missing channel"}, context=context)
    assert not report.passed
    assert report.failures
