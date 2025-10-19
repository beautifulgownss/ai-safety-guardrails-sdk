# AI Safety Guardrails SDK

## 🧠 Overview
AI Safety Guardrails SDK enforces safety and structure around LLM and agent responses with layered validation. It ships with defenses for PII leakage, prompt injection signals, schema enforcement, and rich logging so you can trust every token your agents emit.

## 🚀 Features
- PII detection
- Prompt injection filtering
- Schema and type validation
- Guardrail decorator for wrapping functions or agent responses
- Logging and violation reporting

## 🧩 Architecture
```
Input → Pre-Validation → LLM/Agent → Post-Validation → Output
```

## ⚙️ Quick Start
```python
from guardrails import Guard, ValidationError

guard = Guard(rules=["no_pii", "schema_check"])

@guard
def generate_response(prompt):
    return "My phone number is 555-1234"

try:
    result = generate_response("Tell me about your service")
except ValidationError as e:
    print("Guardrail triggered:", e)
```

## 🧪 Testing
Run the test suite to validate guardrail rules:
```bash
pytest
```

## 🧰 Tech Stack
Python · Regex · Pydantic · Logging

## 🧠 Skills Demonstrated
- AI Safety and Reliability
- SDK Architecture Design
- Input/Output Validation
- Modular Python Engineering

## 🎥 Demo
- Loom walkthrough: _coming soon_
- Explore ready-to-run examples in `examples/`
