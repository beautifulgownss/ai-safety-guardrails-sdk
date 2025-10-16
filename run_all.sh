#!/bin/bash
# ============================================================
#  AI Safety Guardrails SDK - Universal Dev Launcher
# ============================================================
#  Automatically runs:
#    1. FastAPI backend on port 8000
#    2. Next.js dashboard on port 3003
#  Works no matter where you launch it from.
# ============================================================

set -e

# --- Detect project root automatically ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Colors ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🔧 Project root detected: ${SCRIPT_DIR}${NC}"

# --- Step 1: Start FastAPI backend ---
if [ -d "venv" ]; then
  source venv/bin/activate
  echo -e "${GREEN}✅ Virtual environment activated.${NC}"
else
  echo -e "${RED}❌ No venv found. Create it with:${NC}"
  echo "python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn"
  exit 1
fi

echo -e "${CYAN}🚀 Starting FastAPI backend on port 8000...${NC}"
(uvicorn src.safety_sdk.main:app --reload > backend.log 2>&1 &) 
sleep 3

# --- Step 2: Start Next.js dashboard ---
if [ -d "ai-safety-dashboard" ]; then
  cd ai-safety-dashboard
  echo -e "${CYAN}🎨 Starting Next.js dashboard on port 3003...${NC}"
  npx next dev -p 3003
else
  echo -e "${RED}❌ Could not find ai-safety-dashboard directory!${NC}"
  exit 1
fi
