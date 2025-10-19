"""Core guardrail decorator implementation."""

from __future__ import annotations

import functools
from typing import Any, Callable, Iterable, List, Optional, Sequence

from pydantic import ValidationError as PydanticValidationError

from .logger import guard_logger
from .pii_detector import detect_pii
from .schema_validator import validate_with_schema


class ValidationError(Exception):
    """Raised when a guardrail rule fails."""

    def __init__(
        self,
        message: str,
        *,
        rule: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.rule = rule
        self.details = details


RuleCallable = Callable[[Any, str], None]


class Guard:
    """Decorator that enforces guardrail rules around callable execution."""

    def __init__(
        self,
        *,
        rules: Optional[Sequence[Callable[[Any], None] | str]] = None,
        schema: Any = None,
        logger=guard_logger,
    ) -> None:
        self.schema = schema
        self.logger = logger
        self._rules_config = list(rules or [])
        self._validators: List[RuleCallable] = [
            self._resolve_rule(rule) for rule in self._rules_config
        ]

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap the callable with guardrail enforcement."""

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            self.logger.debug("Running pre-validation for %s", func.__name__)
            self._run_validators(payload={"args": args, "kwargs": kwargs}, stage="pre")
            result = func(*args, **kwargs)
            self.logger.debug("Running post-validation for %s", func.__name__)
            self._run_validators(payload=result, stage="post")
            return result

        return wrapped

    def validate(self, payload: Any, *, stage: str = "post") -> None:
        """Manually trigger validation for arbitrary payloads."""
        self._run_validators(payload=payload, stage=stage)

    # Built-in rules -----------------------------------------------------
    def _rule_no_pii(self, payload: Any, stage: str) -> None:
        """Ensure that no personally identifiable information is present."""
        if stage != "post":
            return
        matches = detect_pii(payload)
        if matches:
            raise ValidationError(
                "PII detected in output.",
                rule="no_pii",
                details={"matches": matches},
            )

    def _rule_schema_check(self, payload: Any, stage: str) -> None:
        """Validate payload against the configured schema."""
        if stage != "post":
            return
        try:
            validate_with_schema(payload, self.schema)
        except PydanticValidationError as exc:  # pragma: no cover - error path
            raise ValidationError(
                "Schema validation failed.",
                rule="schema_check",
                details=exc.errors(),
            ) from exc

    # Internal helpers ---------------------------------------------------
    def _resolve_rule(self, rule: Callable[[Any], None] | str) -> RuleCallable:
        if isinstance(rule, str):
            method_name = f"_rule_{rule}"
            validator = getattr(self, method_name, None)
            if validator is None:
                raise ValueError(f"Unknown guardrail rule: {rule!r}")
            return validator
        if callable(rule):
            return lambda payload, stage: rule(payload)  # type: ignore[arg-type]
        raise TypeError("Rules must be callables or registered rule names.")

    def _run_validators(self, *, payload: Any, stage: str) -> None:
        for validator in self._validators:
            try:
                validator(payload, stage)
            except ValidationError:
                self.logger.error(
                    "Validation error for stage '%s' with payload: %s",
                    stage,
                    payload,
                )
                raise

