import fs from 'node:fs';
import { AcceptanceCriterion, QAReport, TestArtifact } from './models.js';

export class QAAnalyzer {
  constructor(backend) {
    this.backend = backend;
  }

  async analyze(criteria, artifact) {
    const results = [];
    for (const criterion of criteria) {
      results.push(await this.backend.evaluate(criterion, artifact));
    }
    return new QAReport(results);
  }

  updateTestCases(report, testCaseText) {
    const additions = ['\n# Auto-updated checks from multimodal QA analysis'];
    for (const result of report.results) {
      additions.push(`- [${result.status.toUpperCase()}] ${result.criterion.id}: ${result.recommendedTestUpdate}`);
    }
    return `${testCaseText.trimEnd()}\n${additions.join('\n')}\n`;
  }
}

export function loadCriteria(path) {
  const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
  return data.criteria.map((item) => new AcceptanceCriterion(item));
}

export function loadArtifact(path) {
  const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
  return new TestArtifact(data);
}
