# Automating QA analysis with multimodal reasoning (local-first)

This project provides a practical way to reduce brittle selector-only assertions by combining:

- Acceptance criteria from docs/user stories.
- Runtime test artifacts (observed text, DOM snapshot, optional screenshot metadata).
- A pluggable reasoning backend:
  - `mock` (no LLM, deterministic and offline)
  - `ollama` (local LLM via `ollama serve`)

It can also auto-update test-case text with outcome-oriented recommendations.

## Why this helps

Traditional Playwright assertions can break when selectors or page structure change. This tool focuses on **intent-level verification** by mapping test outcomes against acceptance criteria and generating test maintenance suggestions.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run in fully local mock mode (no LLM)

```bash
qa-automator \
  --criteria examples/acceptance_criteria.json \
  --artifact examples/test_artifact.json \
  --backend mock \
  --test-case examples/test_case.md \
  --updated-test-case-out examples/updated_test_case.md
```

### Run with local Ollama

1. Start Ollama and pull a model:

```bash
ollama serve
ollama pull llama3.1:8b
```

2. Run analysis:

```bash
qa-automator \
  --criteria examples/acceptance_criteria.json \
  --artifact examples/test_artifact.json \
  --backend ollama \
  --model llama3.1:8b \
  --host http://localhost:11434
```

## Data formats

### Acceptance criteria JSON

```json
{
  "criteria": [
    {"id": "AC-1", "statement": "User can submit login form and see dashboard welcome message"}
  ]
}
```

### Test artifact JSON

```json
{
  "title": "Login flow run #32",
  "observed_text": "Welcome back, Jamie. Dashboard loaded successfully.",
  "dom_snapshot": "<main>...</main>",
  "screenshot_path": "optional/path.png"
}
```

## Extending

- Integrate with Playwright/Cypress by exporting run artifacts to the JSON schema.
- Replace `MockBackend` scoring logic with richer rule-based checks.
- Add CI job that runs mock mode for deterministic triage, and optionally ollama mode for deeper analysis.
