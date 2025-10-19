"""Schema validation rule using Pydantic models."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Type, Union

from pydantic import BaseModel, ValidationError, create_model

from ..core.guard import BaseRule, GuardConfigurationError, RuleContext, RuleResult, Stage

SchemaType = Union[Type[BaseModel], BaseModel, Mapping[str, Any]]


def _model_from_schema(schema: SchemaType) -> Type[BaseModel]:
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema
    if isinstance(schema, BaseModel):
        return schema.__class__
    if isinstance(schema, Mapping):
        fields = {key: (annotation, ...) for key, annotation in schema.items()}
        return create_model("GuardrailsSchema", **fields)  # type: ignore[arg-type]
    raise GuardConfigurationError("Unsupported schema type supplied to SchemaRule.")


class SchemaRule(BaseRule):
    """Validates payloads against a Pydantic schema."""

    severity = "high"

    def __init__(
        self,
        schema: SchemaType,
        *,
        name: Optional[str] = None,
        stages: Sequence[Stage] = ("post",),
        strict: bool = True,
    ) -> None:
        super().__init__(name=name, stages=stages)
        self.model = _model_from_schema(schema)
        self.strict = strict

    def evaluate(self, payload: Any, context: RuleContext, stage: Stage) -> RuleResult:
        try:
            validated = self.model.model_validate(payload)
            details: Dict[str, Any] = {}
            if self.strict:
                details["validated"] = validated.model_dump()
            return RuleResult(
                rule=self.name,
                passed=True,
                stage=stage,
                severity=self.severity,
                details=details,
            )
        except ValidationError as exc:
            return RuleResult(
                rule=self.name,
                passed=False,
                stage=stage,
                severity=self.severity,
                details={"errors": exc.errors()},
            )

