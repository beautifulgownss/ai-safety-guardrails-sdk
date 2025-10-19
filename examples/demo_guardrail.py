"""Minimal demonstration of the AI Safety Guardrails SDK."""

from guardrails import Guard, ValidationError
from guardrails.logger import guard_logger
from pydantic import BaseModel


class ResponseSchema(BaseModel):
    message: str


guard = Guard(rules=["no_pii", "schema_check"], schema=ResponseSchema)


@guard
def generate_service_response(prompt: str) -> dict:
    """Simulate an unsafe model response that leaks PII."""
    return {"message": "Sure, call me at 555-1234 to get started."}


def main() -> None:
    try:
        generate_service_response("Tell me about your premium tier")
    except ValidationError as exc:
        guard_logger.error("Guardrail triggered: %s", exc)
        if getattr(exc, "details", None):
            guard_logger.error("Details: %s", exc.details)

    safe_payload = {"message": "Learn more at example.com/safety"}
    guard.validate(safe_payload)
    print("All checks passed:", safe_payload["message"])


if __name__ == "__main__":
    main()
