# 🧠 AI Safety Guardrails SDK

### A full-stack framework for analyzing, detecting, and visualizing hallucinations in LLM responses.

---

## 🚀 Overview
**AI Safety Guardrails SDK** is a lightweight FastAPI-based backend and a modern Next.js + Tailwind dashboard that work together to evaluate AI model outputs for factual consistency.  
It provides an extensible JSON schema for safety checks and a clean UI for rapid experimentation.

| Component | Description |
|------------|--------------|
| **Backend** | FastAPI service exposing `/api/detect` for hallucination and confidence analysis |
| **Frontend** | Next.js 15 App-Router dashboard with Tailwind 4 styling |
| **Use Case** | Developers evaluating LLM reliability, AI agents, or prompt pipelines |

---

## 🧩 Architecture

    ┌──────────────────────────┐
    │     Next.js Dashboard    │  ← Context + Response inputs
    └────────────┬─────────────┘
                 │ POST /api/detect
                 ▼
    ┌──────────────────────────┐
    │     FastAPI Backend      │  ← Analysis logic, scoring, summary
    └────────────┬─────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │   AI Safety SDK Core     │  ← Guardrails, metrics, and extensions
    └──────────────────────────┘

---

## 🧰 Tech Stack
- **Frontend:** Next.js 15 (App Router), React 18, Tailwind 4, TypeScript  
- **Backend:** FastAPI (Python 3.13)  
- **Infrastructure:** Uvicorn dev server  
- **Version Control:** Git + GitHub  

---

## ⚙️ Local Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/beautifulgownss/ai-safety-guardrails-sdk.git
cd ai-safety-guardrails-sdk
