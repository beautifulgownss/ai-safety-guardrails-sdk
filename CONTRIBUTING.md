# Contributing to AI Safety Guardrails SDK

We welcome contributions from AI/ML engineers, safety researchers, and product teams. This guide walks through the process for proposing changes, implementing features, and shipping polished releases.

## Getting Started
- Fork the repository and create a feature branch from `main` (`feat/short-description`).
- Install dependencies:
  ```bash
  pip install -e .[dev]
  ```
- Ensure your Python version is 3.8 or newer (3.11+ recommended).

## Development Workflow
- Write typed, well-documented Python. Follow PEP 8 and prefer composition over inheritance when feasible.
- Group code into `core`, `rules`, `audit`, and `dashboard` modules to preserve separation of concerns.
- Keep public APIs backwards compatible. Breaking changes must go through an RFC issue first.
- Add or update examples in `examples/` when introducing new features.

## Testing & Quality Gates
Run locally before opening a PR:
```bash
pytest --maxfail=1 --disable-warnings
pytest --asyncio-mode=auto
ruff check .
mypy src
```

PRs must include tests that cover new functionality. Use descriptive assertion messages and prefer deterministic fixtures.

## Documentation Standards
- Update `README.md` and `docs/` with user-facing changes.
- Inline code comments should clarify reasoning, not restate the obvious.
- Every public class or function requires a docstring with usage context.

## Commit & PR Guidelines
- Commit messages: `type(scope): short summary` (e.g., `feat(rules): add pii allowlist`).
- Reference GitHub issues in the PR description when applicable.
- Highlight security-impacting changes and provide mitigation details.
- Request a review from the `@ai-safety-guardrails/maintainers` team.

## Security & Responsible Disclosure
If you discover a vulnerability:
1. Do **not** open a public issue.
2. Email `security@ai-safety-guardrails.dev` with steps to reproduce.
3. Allow 30 days for investigation and coordinated disclosure.

## Release Process
- Versioning follows [Semantic Versioning](https://semver.org/).
- Create a changelog entry under `docs/changelog.md` for every release candidate.
- Tag releases as `vMAJOR.MINOR.PATCH` and publish to PyPI using `build` + `twine` (see `run_backend.sh` for environment setup hints).

Thank you for building safer AI systems with us! 💙
