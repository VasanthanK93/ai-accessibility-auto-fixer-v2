from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .models import AcceptanceCriterion, CriterionResult, TestArtifact


class AnalysisBackend:
    def evaluate(
        self, criterion: AcceptanceCriterion, artifact: TestArtifact
    ) -> CriterionResult:
        raise NotImplementedError


@dataclass
class MockBackend(AnalysisBackend):
    """No-LLM deterministic analyzer for fully-local/offline runs."""

    pass_threshold: float = 0.6

    def evaluate(
        self, criterion: AcceptanceCriterion, artifact: TestArtifact
    ) -> CriterionResult:
        haystack = f"{artifact.observed_text} {artifact.dom_snapshot}".lower()
        terms = [t for t in re.findall(r"[a-zA-Z0-9]+", criterion.statement.lower()) if len(t) > 2]
        if not terms:
            score = 0.0
        else:
            hits = sum(1 for t in terms if t in haystack)
            score = hits / len(terms)

        passed = score >= self.pass_threshold
        status = "pass" if passed else "fail"
        reasoning = (
            f"Matched {round(score * 100, 1)}% of criterion terms against observed output "
            f"using deterministic keyword scoring."
        )
        recommended_update = (
            "Keep existing assertions; add semantic snapshot checks for this flow."
            if passed
            else "Update test case with outcome-oriented checks, and include missing user-visible behavior from acceptance criterion."
        )
        return CriterionResult(
            criterion=criterion,
            status=status,
            confidence=round(score, 3),
            reasoning=reasoning,
            recommended_test_update=recommended_update,
        )


@dataclass
class OllamaBackend(AnalysisBackend):
    """LLM-assisted analyzer using a local Ollama endpoint."""

    model: str = "llama3.1:8b"
    host: str = "http://localhost:11434"
    timeout_seconds: int = 60

    def evaluate(
        self, criterion: AcceptanceCriterion, artifact: TestArtifact
    ) -> CriterionResult:
        prompt = self._build_prompt(criterion, artifact)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        response_text = self._post_json(f"{self.host}/api/generate", payload)
        data = self._parse_model_output(response_text)

        return CriterionResult(
            criterion=criterion,
            status=data.get("status", "fail"),
            confidence=float(data.get("confidence", 0.0)),
            reasoning=data.get("reasoning", "No reasoning returned."),
            recommended_test_update=data.get(
                "recommended_test_update", "No update recommendation returned."
            ),
        )

    def _build_prompt(self, criterion: AcceptanceCriterion, artifact: TestArtifact) -> str:
        screenshot_summary = "No screenshot provided."
        if artifact.screenshot_path and artifact.screenshot_path.exists():
            size = artifact.screenshot_path.stat().st_size
            screenshot_summary = f"Screenshot present: {artifact.screenshot_path.name} ({size} bytes)"

        image_b64 = ""
        if artifact.screenshot_path and artifact.screenshot_path.exists():
            image_b64 = base64.b64encode(artifact.screenshot_path.read_bytes()).decode("utf-8")[:1200]

        return (
            "You are a QA analyst. Evaluate if the artifact satisfies the acceptance criterion. "
            "Return ONLY JSON with keys: status(pass/fail), confidence(0-1), reasoning, recommended_test_update.\n\n"
            f"Criterion: {criterion.statement}\n"
            f"Observed text: {artifact.observed_text}\n"
            f"DOM snapshot: {artifact.dom_snapshot[:3000]}\n"
            f"Image summary: {screenshot_summary}\n"
            f"Image(base64-prefix): {image_b64}\n"
        )

    def _post_json(self, url: str, payload: dict) -> str:
        req = urllib.request.Request(
            url,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Failed to connect to Ollama at {self.host}. Is `ollama serve` running?"
            ) from exc

        parsed = json.loads(body)
        return parsed.get("response", "{}")

    def _parse_model_output(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "status": "fail",
                "confidence": 0.0,
                "reasoning": f"Model response was not valid JSON: {text[:200]}",
                "recommended_test_update": "Retry with stricter prompt or fallback to mock backend.",
            }
