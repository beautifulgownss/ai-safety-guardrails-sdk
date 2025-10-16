from fastapi import FastAPI

app = FastAPI(title="AI Safety Guardrails SDK")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FastAPI backend is running"}

@app.post("/api/detect")
def detect_hallucination(data: dict):
    # simple mock response until your real SDK logic is wired up
    return {
        "hallucination_sections": [
            {"claim": "Mock claim", "status": "supported", "confidence": 1.0}
        ],
        "overall_confidence": 1.0,
        "hallucination_score": 0.0,
        "summary": "This is a mock response from your backend."
    }
