"""Machine-learning powered guard implementations."""
from __future__ import annotations

from statistics import mean
from typing import Any, Dict, Iterable, Optional

from .base import Guard, GuardResponse, GuardResult
from ..ml_models import create_ner_pipeline, map_entities_to_pii_types


class MLPIIDetectorGuard(Guard):
    """Detect personally identifiable information using a transformer NER model.

    Parameters
    ----------
    config:
        Supported keys:
        - ``model_name_or_path`` (str): Hugging Face model identifier or local path.
        - ``aggregation_strategy`` (str): Passed directly to ``transformers.pipeline``.
        - ``device`` (int): Device index for the pipeline (``-1`` for CPU).
        - ``threshold`` (float): Minimum entity score to keep (default ``0.75``).
        - ``action`` (str): ``"block"`` or ``"warn"`` when PII is found (default ``"warn"``).
    pipeline:
        Optional, pre-created Hugging Face NER pipeline. Supply this when running in
        environments without internet access or when sharing a cached model between guards.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        pipeline: Optional[Any] = None,
    ) -> None:
        super().__init__(config)
        self.action = self.config.get("action", "warn")
        self.threshold = float(self.config.get("threshold", 0.75))
        self._pipeline = pipeline
        if self._pipeline is None:
            self._pipeline = self._load_pipeline()

    @property
    def name(self) -> str:
        return "ml_pii_detector"

    def check_input(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GuardResponse:
        if not prompt:
            return GuardResponse(result=GuardResult.ALLOW)

        entities = self._run_pipeline(prompt)
        pii_findings = map_entities_to_pii_types(entities)

        if not pii_findings:
            return GuardResponse(result=GuardResult.ALLOW)

        confidence = _average_score(entities)
        response = GuardResponse(
            result=GuardResult.BLOCK if self.action == "block" else GuardResult.WARN,
            reason=f"PII detected: {sorted(pii_findings.keys())}",
            confidence=confidence,
            metadata={"pii_types": pii_findings},
        )
        return response

    def check_output(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GuardResponse:
        return self.check_input(response, context)

    def _load_pipeline(self):
        model_name = self.config.get("model_name_or_path")
        if not model_name:
            raise ValueError(
                "MLPIIDetectorGuard requires `model_name_or_path` when a pipeline is not provided."
            )
        aggregation = self.config.get("aggregation_strategy", "simple")
        device = int(self.config.get("device", -1))
        return create_ner_pipeline(model_name, aggregation, device)

    def _run_pipeline(self, prompt: str) -> Iterable[Dict[str, Any]]:
        predictions = self._pipeline(prompt)
        return [p for p in predictions if float(p.get("score", 0.0)) >= self.threshold]


def _average_score(entities: Iterable[Dict[str, Any]]) -> float:
    scores = [float(entity.get("score", 0.0)) for entity in entities if "score" in entity]
    return mean(scores) if scores else 1.0
