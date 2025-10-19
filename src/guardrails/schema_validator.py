"""Schema validation utilities built on top of Pydantic."""

from __future__ import annotations

from typing import Any, Optional, Type, Union

from pydantic import BaseModel, ValidationError as PydanticValidationError, create_model

SchemaType = Union[Type[BaseModel], BaseModel, dict]


def _model_from_schema(schema: SchemaType) -> Type[BaseModel]:
    """Convert supported schema formats into a Pydantic model class."""
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema
    if isinstance(schema, BaseModel):
        return schema.__class__
    if isinstance(schema, dict):
        fields = {
            key: (value, ...) for key, value in schema.items()
        }
        return create_model("DynamicSchema", **fields)  # type: ignore[arg-type]
    raise TypeError("Unsupported schema type for guardrails validation.")


def validate_with_schema(
    data: Any, schema: Optional[SchemaType]
) -> None:
    """Validate arbitrary data against the provided schema."""
    if schema is None:
        return
    model = _model_from_schema(schema)
    try:
        model.model_validate(data)
    except PydanticValidationError as exc:
        raise exc

