"""Minimal CLI demo showcasing guardrail enforcement."""

from guardrails import (
    Guard,
    GuardViolation,
    InjectionRule,
    PIIRule,
    SchemaRule,
    StdoutAuditLogger,
)
from pydantic import BaseModel


class ResponseSchema(BaseModel):
    message: str
    channel: str


guard = Guard(
    rules=[PIIRule(), InjectionRule(), SchemaRule(ResponseSchema)],
    audit_logger=StdoutAuditLogger(),
)


@guard.protect
def generate_service_response(prompt: str) -> dict:
    return {
        "message": "Sure, call me at 555-1234 to get started.",
        "channel": "voice",
    }


def main() -> None:
    try:
        generate_service_response("Tell me about your premium tier")
    except GuardViolation as exc:
        print("Guardrail triggered:")
        for failure in exc.results:
            print(f"- {failure.rule}: {failure.details}")

    safe_payload = {"message": "Learn more at example.com/safety", "channel": "web"}
    report = guard.check(safe_payload)
    print("Post-validation report passed:", report.passed)


if __name__ == "__main__":
    main()
