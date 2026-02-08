import test from 'node:test';
import assert from 'node:assert/strict';

import { QAAnalyzer } from '../src/analyzer.js';
import { MockBackend } from '../src/backends.js';
import { AcceptanceCriterion, TestArtifact } from '../src/models.js';

test('mock backend evaluates criteria and updates test case', async () => {
  const criteria = [
    new AcceptanceCriterion({ id: 'AC-1', statement: 'dashboard welcome message visible' }),
    new AcceptanceCriterion({ id: 'AC-2', statement: 'invalid credentials shows error banner' })
  ];

  const artifact = new TestArtifact({
    title: 'Run',
    observed_text: 'Dashboard loaded and welcome message visible',
    dom_snapshot: '<h1>Dashboard</h1><p>Welcome message visible</p>'
  });

  const analyzer = new QAAnalyzer(new MockBackend());
  const report = await analyzer.analyze(criteria, artifact);

  assert.equal(report.results.length, 2);
  assert.equal(report.results[0].status, 'pass');
  assert.equal(report.results[1].status, 'fail');

  const updated = analyzer.updateTestCases(report, '# Case');
  assert.match(updated, /Auto-updated checks/);
  assert.match(updated, /AC-1/);
  assert.match(updated, /AC-2/);
});
