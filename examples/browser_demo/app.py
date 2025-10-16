"""FastAPI demo for trying the ML PII guard in a browser."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from safety_sdk.guards import GuardResponse, MLPIIDetectorGuard


def _create_guard() -> MLPIIDetectorGuard:
    model_name = os.getenv("PII_MODEL_NAME", "dslim/bert-base-NER")
    threshold = float(os.getenv("PII_THRESHOLD", "0.70"))
    return MLPIIDetectorGuard(
        {
            "model_name_or_path": model_name,
            "threshold": threshold,
            "action": "warn",
        }
    )


def _serialize_response(response: GuardResponse) -> Dict[str, object]:
    metadata = response.metadata or {}
    pii_map = metadata.get("pii_types") or {}

    normalized: Dict[str, List[str]] = {}
    for pii_type, values in pii_map.items():
        unique_tokens = sorted({value.strip() for value in values if value})
        if unique_tokens:
            normalized[pii_type] = unique_tokens

    return {
        "result": response.result.value,
        "reason": response.reason,
        "confidence": round(float(response.confidence), 3),
        "pii_types": normalized,
    }


app = FastAPI(title="AI Safety Guardrails Browser Demo")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
pii_guard = _create_guard()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "submitted_text": "",
        },
    )


@app.post("/scan", response_class=HTMLResponse)
async def scan_text(request: Request, text: str = Form("") ) -> HTMLResponse:
    error: str | None = None
    result_payload: Dict[str, object] | None = None

    try:
        response = pii_guard.check_input(text or "")
        result_payload = _serialize_response(response)
    except Exception as exc:  # pragma: no cover - surfaced in UI
        error = str(exc)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result_payload,
            "error": error,
            "submitted_text": text,
        },
    )
