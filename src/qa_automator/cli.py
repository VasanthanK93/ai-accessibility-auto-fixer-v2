from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import QAAnalyzer, load_artifact, load_criteria
from .backends import MockBackend, OllamaBackend


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automate QA analysis with multimodal reasoning and test updates"
    )
    parser.add_argument("--criteria", required=True, type=Path, help="JSON file with criteria")
    parser.add_argument("--artifact", required=True, type=Path, help="JSON file with test run artifact")
    parser.add_argument("--backend", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--model", default="llama3.1:8b")
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--test-case", type=Path, help="Existing test-case markdown/txt to update")
    parser.add_argument(
        "--updated-test-case-out",
        type=Path,
        default=Path("updated_test_case.md"),
        help="Output path for updated test case",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    backend = (
        MockBackend()
        if args.backend == "mock"
        else OllamaBackend(model=args.model, host=args.host)
    )
    analyzer = QAAnalyzer(backend=backend)

    criteria = load_criteria(args.criteria)
    artifact = load_artifact(args.artifact)

    report = analyzer.analyze(criteria, artifact)
    print(json.dumps(report.as_dict(), indent=2))

    if args.test_case:
        baseline = args.test_case.read_text()
        updated = analyzer.update_test_cases(report, baseline)
        args.updated_test_case_out.write_text(updated)
        print(f"\nUpdated test-case written to: {args.updated_test_case_out}")


if __name__ == "__main__":
    main()
