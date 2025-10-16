#!/bin/bash
# ============================================================
#  AI Safety Guardrails SDK - FastAPI Backend Runner
# ============================================================
#  This script activates the venv, installs dependencies if missing,
#  ensures CORS is configured, and runs Uvicorn in autoreload mode.
# ============================================================

# Exit on errors
set -e

# --- Helper colors for output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting AI Safety Guardrails SDK Backend...${NC}"

# --- Step 1: Activate virtual environment ---
if [ -d "venv" ]; then
  source venv/bin/activate
  echo -e "${GREEN}Virtual environment activated.${NC}"
else
  echo -e "${YELLOW}No venv found. Creating one...${NC}"
  python3 -m venv venv
  source venv/bin/activate
fi

# --- Step 2: Install dependencies if needed ---
echo -e "${CYAN}Checking for required packages...${NC}"
pip install --quiet --upgrade pip
pip install --quiet fastapi uvicorn "python-dotenv" "fastapi-cors"

# --- Step 3: Verify backend entrypoint exists ---
MAIN_FILE="src/safety_sdk/main.py"
if [ ! -f "$MAIN_FILE" ]; then
  echo -e "${YELLOW}No main.py found, creating default FastAPI entrypoint...${NC}"
  mkdir -p src/safety_sdk
  cat > "$MAIN_FILE" << 'PYCODE'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Safety Guardrails SDK")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FastAPI backend is running"}

@app.post("/api/detect")
def detect_hallucination(data: dict):
    # simple mock response until real SDK logic is wired up
    return {
        "hallucination_sections": [
            {"claim": "Mock claim", "status": "supported", "confidence": 1.0}
        ],
        "overall_confidence": 1.0,
        "hallucination_score": 0.0,
        "summary": "Mock response from backend"
    }
PYCODE
  echo -e "${GREEN}Created default FastAPI main.py with CORS.${NC}"
fi

# --- Step 4: Run Uvicorn ---
echo -e "${CYAN}Launching Uvicorn on http://127.0.0.1:8000 ...${NC}"
uvicorn src.safety_sdk.main:app --reload
