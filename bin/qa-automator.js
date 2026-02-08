#!/usr/bin/env node
import fs from 'node:fs';
import { QAAnalyzer, loadArtifact, loadCriteria } from '../src/analyzer.js';
import { MockBackend, OllamaBackend } from '../src/backends.js';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key.startsWith('--')) {
      args[key.slice(2)] = value;
      i += 1;
    }
  }
  return args;
}

function requireArg(args, key) {
  if (!args[key]) {
    throw new Error(`Missing required argument: --${key}`);
  }
}

async function main() {
  const args = parseArgs(process.argv);
  requireArg(args, 'criteria');
  requireArg(args, 'artifact');

  const backendName = args.backend || 'mock';
  const backend =
    backendName === 'ollama'
      ? new OllamaBackend({ model: args.model || 'llama3.1:8b', host: args.host || 'http://localhost:11434' })
      : new MockBackend();

  const analyzer = new QAAnalyzer(backend);
  const criteria = loadCriteria(args.criteria);
  const artifact = loadArtifact(args.artifact);

  const report = await analyzer.analyze(criteria, artifact);
  console.log(JSON.stringify(report.asDict(), null, 2));

  if (args['test-case']) {
    const baseline = fs.readFileSync(args['test-case'], 'utf-8');
    const updated = analyzer.updateTestCases(report, baseline);
    const outFile = args['updated-test-case-out'] || 'updated_test_case.md';
    fs.writeFileSync(outFile, updated);
    console.log(`\nUpdated test-case written to: ${outFile}`);
  }
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
