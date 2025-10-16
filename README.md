# AI Safety Guardrails SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python SDK for wrapping LLM calls with safety guards, audit logging, and policy enforcement.

## Features

- **🛡️ Multi-Layer Safety Guards**: PII detection (regex + ML), prompt injection protection, role-based access control
- **📝 Audit Logging**: Structured logging of all LLM interactions with security metadata  
- **⚙️ Configurable Policies**: Fine-tune guard sensitivity and fail-open behavior
- **🔌 Provider Agnostic**: Works with OpenAI, Anthropic, or any LLM API
- **🚀 Zero-Config Start**: Simple decorator pattern for immediate protection

## Quick Start

### Installation

```bash
pip install -e .  # Local development install
# Optional extras:
#   pip install -e '.[demo]'   # Browser demo and ML guard dependencies
#   pip install -e '.[full]'   # OpenAI + jsonschema integrations
```

### Basic Usage

```python
from safety_sdk import safe_llm, SafetyConfig, PIIDetectorGuard, InjectionDetectorGuard

# Configure safety guards
guards = [
    PIIDetectorGuard({'action': 'block'}),
    InjectionDetectorGuard({'sensitivity': 'medium'})
]

config = SafetyConfig(
    guards=guards,
    user_id="your_user_id",
    role="developer"
)

# Wrap your LLM function
@safe_llm(config)
def safe_openai_call(messages, **kwargs):
    return openai.ChatCompletion.create(messages=messages, **kwargs)

# Use normally - guards run automatically
try:
    response = safe_openai_call([
        {"role": "user", "content": "What is the capital of France?"}
    ])
    print(response.choices[0].message.content)
except SafetyException as e:
    print(f"Request blocked: {e}")
```

## Guard Types

### PII Detector
Detects and optionally blocks personally identifiable information:
- Email addresses, phone numbers, SSNs
- Configurable action: `'warn'`, `'block'`, or `'mask'`

### ML PII Detector (Preview)
Transformer-backed named entity recognition guard for higher recall:
- Configure `model_name_or_path`, scoring thresholds, and action (`'warn'` or `'block'`).
- Accepts a pre-loaded Hugging Face pipeline for offline or cached inference.
- Ideal for showcasing -level ML integration alongside classical regex checks.

```python
from safety_sdk import MLPIIDetectorGuard

ml_guard = MLPIIDetectorGuard({
    "model_name_or_path": "dslim/bert-base-NER",
    "action": "block",
    "threshold": 0.8,
})
```

### Injection Detector  
Protects against prompt injection attacks:
- Pattern matching for common injection techniques
- Configurable sensitivity: `'low'`, `'medium'`, or `'high'`

### RBAC Guard
Role-based access control for sensitive operations:
- Define permissions per user role
- Block unauthorized database/system operations

## Examples

Run the included examples:

```bash
python examples/pii_safe_extraction.py
python examples/safe_tool_use.py
python examples/comprehensive_safety.py
```

### Browser-based ML guard demo

Launch a FastAPI-powered playground to try the ML PII detector from your browser:

```bash
pip install -e '.[demo]'
uvicorn examples.browser_demo.app:app --reload
```

Open <http://127.0.0.1:8000> to paste prompts or responses and inspect which entities the transformer model flags as PII. Set
`PII_MODEL_NAME` and `PII_THRESHOLD` environment variables before starting the server to customise the model or detection
sensitivity.

## Development

### Adding Custom Guards

```python
from safety_sdk.guards.base import Guard, GuardResponse, GuardResult

class CustomGuard(Guard):
    @property
    def name(self) -> str:
        return "custom_guard"
    
    def check_input(self, prompt: str, context=None) -> GuardResponse:
        if "forbidden_word" in prompt.lower():
            return GuardResponse(
                result=GuardResult.BLOCK,
                reason="Forbidden content detected"
            )
        return GuardResponse(result=GuardResult.ALLOW)
    
    def check_output(self, response: str, context=None) -> GuardResponse:
        return GuardResponse(result=GuardResult.ALLOW)
```

## Use Cases

- **Data Processing**: Safely extract structured data while protecting PII
- **Database Operations**: Role-based access control for SQL operations
- **Content Generation**: Prevent harmful or biased content generation
- **API Orchestration**: Audit and control access to sensitive APIs
- **Compliance**: Meet data protection and access control requirements

## Roadmap

The [Guardrails SDK Roadmap](docs/roadmap.md) outlines the ML upgrades, benchmarking, adversarial testing, and observability work planned for the next development cycles.

## License

MIT License - see LICENSE file for details.
