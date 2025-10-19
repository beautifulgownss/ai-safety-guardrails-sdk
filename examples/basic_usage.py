"""Basic usage example for the AI Safety Guardrails SDK."""

from __future__ import annotations

from typing import Iterable

from guardrails import (
    Guard,
    GuardViolation,
    InjectionRule,
    PIIRule,
    RuleContext,
    SchemaRule,
    StdoutAuditLogger,
)
from pydantic import BaseModel


class SupportResponse(BaseModel):
    message: str
    category: str


def resolve_roles(context: RuleContext) -> Iterable[str]:
    # Hook into your RBAC system to return user roles.
    return context.metadata.get("roles", [])


guard = Guard(
    rules=[
        InjectionRule(),
        PIIRule(),
        SchemaRule(SupportResponse),
    ],
    audit_logger=StdoutAuditLogger(),
    rbac_resolver=resolve_roles,
    name="support_guard",
)


@guard.protect
def handle_ticket(prompt: str) -> dict:
    # Replace with your LLM or agent call.
    return {
        "message": "Reach me at 555-123-4567 so we can continue.",
        "category": "sales",
    }


if __name__ == "__main__":
    try:
        response = handle_ticket("Need help with enterprise plan")
        print("Response:", response)
    except GuardViolation as exc:
        print("Guardrail violation detected:")
        for result in exc.results:
            print(f"- {result.rule}: {result.details}")

    # Manual validation example
    context = RuleContext(inputs={}, metadata={"roles": ["support"]})
    report = guard.check({"message": "Safe", "category": "info"}, context=context)
    print("Manual check passed:", report.passed)
