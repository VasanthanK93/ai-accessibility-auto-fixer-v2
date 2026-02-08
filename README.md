# Automating QA analysis with multimodal reasoning (Node.js, local-first)

This Node.js application reduces brittle selector-only QA assertions by evaluating runtime outcomes against acceptance criteria.

## What it does

- Ingests acceptance criteria from user stories/documents.
- Ingests test artifacts from a run (observed text, DOM snapshot, optional screenshot path).
- Evaluates coverage with pluggable analysis backends:
  - `mock`: deterministic and fully offline (no LLM)
  - `ollama`: local LLM reasoning through `ollama serve`
- Auto-updates test-case files with criterion-level recommendations.

## Install

```bash
npm install
```

## Run (mock mode, no LLM)

```bash
node bin/qa-automator.js \
  --criteria examples/acceptance_criteria.json \
  --artifact examples/test_artifact.json \
  --backend mock \
  --test-case examples/test_case.md \
  --updated-test-case-out examples/updated_test_case.md
```

## Run (Ollama local)

```bash
ollama serve
ollama pull llama3.1:8b

node bin/qa-automator.js \
  --criteria examples/acceptance_criteria.json \
  --artifact examples/test_artifact.json \
  --backend ollama \
  --model llama3.1:8b \
  --host http://localhost:11434
```

## Test

```bash
npm test
```

## Data format

Acceptance criteria:

```json
{
  "criteria": [
    { "id": "AC-1", "statement": "User can submit login form and see dashboard welcome message" }
  ]
}
```

Test artifact:

```json
{
  "title": "Login flow run #32",
  "observed_text": "Welcome back, Jamie. Dashboard loaded successfully.",
  "dom_snapshot": "<main>...</main>",
  "screenshot_path": "optional/path.png"
}
```
