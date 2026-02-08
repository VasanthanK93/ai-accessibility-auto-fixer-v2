from qa_automator.analyzer import QAAnalyzer
from qa_automator.backends import MockBackend
from qa_automator.models import AcceptanceCriterion, TestArtifact


def test_mock_backend_evaluates_and_updates_test_case() -> None:
    criteria = [
        AcceptanceCriterion(id="AC-1", statement="dashboard welcome message visible"),
        AcceptanceCriterion(id="AC-2", statement="invalid credentials shows error banner"),
    ]
    artifact = TestArtifact(
        title="Run",
        observed_text="Dashboard loaded and welcome message visible",
        dom_snapshot="<h1>Dashboard</h1><p>Welcome message visible</p>",
    )

    report = QAAnalyzer(backend=MockBackend()).analyze(criteria, artifact)

    assert len(report.results) == 2
    assert report.results[0].status == "pass"
    assert report.results[1].status == "fail"

    updated = QAAnalyzer(backend=MockBackend()).update_test_cases(report, "# Case")
    assert "Auto-updated checks" in updated
    assert "AC-1" in updated and "AC-2" in updated
