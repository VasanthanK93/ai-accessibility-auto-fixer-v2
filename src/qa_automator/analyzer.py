from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .backends import AnalysisBackend
from .models import AcceptanceCriterion, QAReport, TestArtifact


@dataclass
class QAAnalyzer:
    backend: AnalysisBackend

    def analyze(self, criteria: list[AcceptanceCriterion], artifact: TestArtifact) -> QAReport:
        return QAReport(results=[self.backend.evaluate(c, artifact) for c in criteria])

    def update_test_cases(self, report: QAReport, test_case_text: str) -> str:
        additions: list[str] = ["\n# Auto-updated checks from multimodal QA analysis"]
        for result in report.results:
            additions.append(
                f"- [{result.status.upper()}] {result.criterion.id}: {result.recommended_test_update}"
            )
        return test_case_text.rstrip() + "\n" + "\n".join(additions) + "\n"


def load_criteria(path: Path) -> list[AcceptanceCriterion]:
    data = json.loads(path.read_text())
    return [AcceptanceCriterion(**item) for item in data["criteria"]]


def load_artifact(path: Path) -> TestArtifact:
    data = json.loads(path.read_text())
    screenshot = data.get("screenshot_path")
    return TestArtifact(
        title=data["title"],
        observed_text=data["observed_text"],
        dom_snapshot=data.get("dom_snapshot", ""),
        screenshot_path=Path(screenshot) if screenshot else None,
    )
