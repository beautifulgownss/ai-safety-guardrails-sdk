"""NER utilities for ML-backed PII detection guards."""
from __future__ import annotations

from typing import Dict, Iterable, List
import importlib


def _require_transformers() -> None:
    if importlib.util.find_spec("transformers") is None:
        raise ImportError(
            "The 'transformers' package is required for ML-powered PII detection. "
            "Install it with `pip install transformers` or provide a pre-built pipeline."
        )


def create_ner_pipeline(
    model_name_or_path: str,
    aggregation_strategy: str = "simple",
    device: int = -1,
):
    """Return a Hugging Face NER pipeline using the requested model.

    Parameters
    ----------
    model_name_or_path:
        Hugging Face model identifier or local path.
    aggregation_strategy:
        Aggregation strategy passed to the transformers pipeline.
    device:
        Device index understood by ``transformers.pipeline`` (``-1`` for CPU).
    """
    _require_transformers()
    from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
    return pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy=aggregation_strategy,
        device=device,
    )


def map_entities_to_pii_types(entities: Iterable[Dict[str, str]]) -> Dict[str, List[str]]:
    """Group detected entities into coarse PII categories.

    The mapping intentionally collapses model-specific label schemes (e.g. B-PER, I-EMAIL)
    into a consistent surface area for guard responses.
    """
    pii_map: Dict[str, List[str]] = {}
    for entity in entities:
        label = entity.get("entity_group") or entity.get("entity")
        word = entity.get("word") or entity.get("text")
        if not label or not word:
            continue

        normalized = label.upper()
        pii_type = _normalize_label(normalized)
        if pii_type is None:
            continue

        pii_map.setdefault(pii_type, []).append(word)
    return pii_map


def _normalize_label(label: str) -> str | None:
    if label in {"PER", "PERSON", "B-PER", "I-PER"}:
        return "PERSON"
    if label in {"ORG", "ORGANIZATION", "B-ORG", "I-ORG"}:
        return "ORGANIZATION"
    if label in {"LOC", "GPE", "LOCATION", "B-LOC", "I-LOC"}:
        return "LOCATION"
    if label in {"EMAIL", "B-EMAIL", "I-EMAIL"}:
        return "EMAIL"
    if label in {"PHONE", "B-PHONE", "I-PHONE", "TEL"}:
        return "PHONE"
    if label in {"SSN", "B-SSN", "I-SSN"}:
        return "SSN"
    if label in {"CREDIT_CARD", "CARD", "B-CARD", "I-CARD"}:
        return "CREDIT_CARD"
    if label in {"ADDRESS", "B-ADDRESS", "I-ADDRESS"}:
        return "ADDRESS"
    return None
