"""Tests for the Guard decorator and built-in rules."""

import pytest
from pydantic import BaseModel

from guardrails import Guard, ValidationError


class MessageSchema(BaseModel):
    message: str


def test_guard_allows_clean_output():
    guard = Guard(rules=["no_pii", "schema_check"], schema=MessageSchema)

    @guard
    def safe_response() -> dict:
        return {"message": "All systems operational."}

    assert safe_response()["message"] == "All systems operational."


def test_guard_blocks_pii_detection():
    guard = Guard(rules=["no_pii"])

    @guard
    def unsafe_response() -> str:
        return "Call me at 555-1234 for details."

    with pytest.raises(ValidationError):
        unsafe_response()
