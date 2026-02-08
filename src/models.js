export class AcceptanceCriterion {
  constructor({ id, statement }) {
    this.id = id;
    this.statement = statement;
  }
}

export class TestArtifact {
  constructor({ title, observed_text, dom_snapshot = '', screenshot_path = null }) {
    this.title = title;
    this.observedText = observed_text;
    this.domSnapshot = dom_snapshot;
    this.screenshotPath = screenshot_path;
  }
}

export class CriterionResult {
  constructor({ criterion, status, confidence, reasoning, recommended_test_update }) {
    this.criterion = criterion;
    this.status = status;
    this.confidence = confidence;
    this.reasoning = reasoning;
    this.recommendedTestUpdate = recommended_test_update;
  }

  toJSON() {
    return {
      criterion_id: this.criterion.id,
      statement: this.criterion.statement,
      status: this.status,
      confidence: this.confidence,
      reasoning: this.reasoning,
      recommended_test_update: this.recommendedTestUpdate
    };
  }
}

export class QAReport {
  constructor(results = []) {
    this.results = results;
  }

  asDict() {
    return { results: this.results.map((r) => r.toJSON()) };
  }
}
