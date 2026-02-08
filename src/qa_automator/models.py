from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AcceptanceCriterion:
    """One requirement parsed from document/user-story."""

    id: str
    statement: str


@dataclass
class TestArtifact:
    """Execution traces captured from UI/API test run."""

    __test__ = False

    title: str
    observed_text: str
    dom_snapshot: str = ""
    screenshot_path: Path | None = None


@dataclass
class CriterionResult:
    criterion: AcceptanceCriterion
    status: str
    confidence: float
    reasoning: str
    recommended_test_update: str


@dataclass
class QAReport:
    results: list[CriterionResult] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "results": [
                {
                    "criterion_id": r.criterion.id,
                    "statement": r.criterion.statement,
                    "status": r.status,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning,
                    "recommended_test_update": r.recommended_test_update,
                }
                for r in self.results
            ]
        }
