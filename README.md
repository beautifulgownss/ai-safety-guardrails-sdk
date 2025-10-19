# AI Safety Guardrails SDK

[![PyPI Version](https://img.shields.io/pypi/v/ai-safety-guardrails-sdk.svg)](https://pypi.org/project/ai-safety-guardrails-sdk/) [![Python Versions](https://img.shields.io/pypi/pyversions/ai-safety-guardrails-sdk.svg)](https://pypi.org/project/ai-safety-guardrails-sdk/) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

AI Safety Guardrails SDK is an enterprise-ready toolkit for validating and monitoring large language model (LLM) and agent outputs. It combines deterministic rules, schema enforcement, audit logging, and RBAC-aware workflows so you can safely deploy generative AI inside regulated or high-stakes environments.

---

## Table of Contents
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Rule Catalog](#rule-catalog)
- [Audit, RBAC, and Monitoring](#audit-rbac-and-monitoring)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Development](#development)
- [Contributing](#contributing)

## Key Features
- Multi-stage validation pipeline (`pre` and `post`) for LLM calls and agent workflows.
- Built-in rules for PII detection, prompt injection filtering, and schema/type validation.
- Extensible rule system with typed base classes and configuration hooks.
- Structured audit events with pluggable backends and performance instrumentation.
- RBAC integration points for enforcing rule execution by user or tenant context.
- Production DX: comprehensive tests, dashboard hooks, and real-world examples.

## Architecture
```
Input → Pre-Validation → LLM / Agent Logic → Post-Validation → Output & Audit Trail
```
Each stage can host any number of rules. Rules emit structured `RuleResult` objects which are aggregated into audit logs, performance metrics, and violation reports.

## Installation
Install from PyPI (recommended):
```bash
pip install ai-safety-guardrails-sdk
```

Install from source:
```bash
git clone https://github.com/beautifulgownss/ai-safety-guardrails-sdk.git
cd ai-safety-guardrails-sdk
pip install -e .[dev]
```

## Quick Start
```python
from guardrails import (
    Guard,
    GuardViolation,
    PIIRule,
    InjectionRule,
    SchemaRule,
    StdoutAuditLogger,
    RuleContext,
)
from pydantic import BaseModel


class ResponseSchema(BaseModel):
    message: str
    source: str


guard = Guard(
    rules=[
        PIIRule(),
        InjectionRule(),
        SchemaRule(ResponseSchema),
    ],
    audit_logger=StdoutAuditLogger(),
)


@guard.protect
def generate_reply(prompt: str) -> dict:
    return {"message": "Call me at 555-123-4567", "source": "internal"}


try:
    reply = generate_reply("Tell me about your plans")
except GuardViolation as exc:
    print("Guardrail triggered", exc.results)
else:
    print(reply)
```

### Async Workflows
```python
@guard.protect
async def generate_async(prompt: str) -> dict:
    return {"message": "Safe response", "source": "async"}
```

## Rule Catalog
| Rule | Description | Default Stage | Highlights |
|------|-------------|---------------|------------|
| `PIIRule` | Detects emails, phone numbers, SSNs, credit cards, and IP addresses. | `post` | Allowlist support, configurable match limits. |
| `InjectionRule` | Flags prompt injection attempts and exfiltration tactics. | `pre`, `post` | Heuristic + pluggable detector pipeline. |
| `SchemaRule` | Validates payloads against Pydantic models or typed dicts. | `post` | Supports strict validation with rich error payloads. |

Create custom rules by subclassing `BaseRule` and overriding `evaluate`/`evaluate_async`.

## Audit, RBAC, and Monitoring
- **Audit logging** — Structured `dict` events delivered to any backend by implementing `BaseAuditLogger`. The default `StdoutAuditLogger` writes to Python logging.
- **Performance monitoring** — `PerformanceMonitor` tracks per-rule latency for observability and SLO reporting.
- **RBAC integration** — Supply `rbac_resolver` to `Guard` to enforce rule execution by caller role or tenant. Rules can declare `required_roles` for granular policy control.

## API Reference
```python
class Guard:
    def __init__(
        self,
        rules: Sequence[BaseRule],
        *,
        audit_logger: Optional[BaseAuditLogger] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        rbac_resolver: Optional[Callable[[RuleContext], Iterable[str]]] = None,
    ) -> None

    def protect(self, func: Callable[..., Any]) -> Callable[..., Any]
    def check(self, payload: Any, *, stage: Literal["pre", "post"], context: Optional[RuleContext] = None) -> GuardReport
    async def check_async(self, payload: Any, *, stage: Literal["pre", "post"], context: Optional[RuleContext] = None) -> GuardReport
```

```python
class BaseRule(ABC):
    def evaluate(self, payload: Any, context: RuleContext, stage: Literal["pre", "post"]) -> RuleResult
    async def evaluate_async(self, payload: Any, context: RuleContext, stage: Literal["pre", "post"]) -> RuleResult
```

Refer to `docs/` for extended API coverage, configuration samples, and dashboard integration guides.

## Examples
- `examples/basic_usage.py` — End-to-end example with guard enforcement and structured error handling.
- `examples/demo_guardrail.py` — CLI demo of guard violations and compliant responses.

## Development
- Requirements are listed in `requirements.txt` and `setup.py` extras.
- Run the test suite with:
  ```bash
  pytest
  ```
- Run lint and type checks:
  ```bash
  ruff check .
  mypy src
  ```
- Launch the optional dashboard or backend tooling with `run_backend.sh` once dependencies are installed.

## Contributing
We welcome security researchers, AI/ML engineers, and product teams. Please review [CONTRIBUTING.md](CONTRIBUTING.md) for branching, testing, and code review expectations.

---

**Need support?** Open a GitHub Issue or reach out via the project discussions tab.
