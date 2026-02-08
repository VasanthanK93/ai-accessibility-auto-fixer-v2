import fs from 'node:fs';
import { CriterionResult } from './models.js';

export class MockBackend {
  constructor({ passThreshold = 0.6 } = {}) {
    this.passThreshold = passThreshold;
  }

  evaluate(criterion, artifact) {
    const haystack = `${artifact.observedText} ${artifact.domSnapshot}`.toLowerCase();
    const terms = (criterion.statement.toLowerCase().match(/[a-z0-9]+/g) || []).filter(
      (t) => t.length > 2
    );

    const score = terms.length === 0 ? 0 : terms.filter((t) => haystack.includes(t)).length / terms.length;
    const passed = score >= this.passThreshold;

    return new CriterionResult({
      criterion,
      status: passed ? 'pass' : 'fail',
      confidence: Number(score.toFixed(3)),
      reasoning: `Matched ${(score * 100).toFixed(1)}% of criterion terms against observed output using deterministic keyword scoring.`,
      recommended_test_update: passed
        ? 'Keep existing assertions; add semantic snapshot checks for this flow.'
        : 'Update test case with outcome-oriented checks, and include missing user-visible behavior from acceptance criterion.'
    });
  }
}

export class OllamaBackend {
  constructor({ model = 'llama3.1:8b', host = 'http://localhost:11434', timeoutMs = 60000 } = {}) {
    this.model = model;
    this.host = host;
    this.timeoutMs = timeoutMs;
  }

  async evaluate(criterion, artifact) {
    const prompt = this.#buildPrompt(criterion, artifact);
    const responseText = await this.#postJson(`${this.host}/api/generate`, {
      model: this.model,
      prompt,
      stream: false,
      format: 'json'
    });

    const data = this.#parseModelOutput(responseText);
    return new CriterionResult({
      criterion,
      status: data.status || 'fail',
      confidence: Number(data.confidence || 0),
      reasoning: data.reasoning || 'No reasoning returned.',
      recommended_test_update: data.recommended_test_update || 'No update recommendation returned.'
    });
  }

  #buildPrompt(criterion, artifact) {
    let screenshotSummary = 'No screenshot provided.';
    let imagePrefix = '';

    if (artifact.screenshotPath && fs.existsSync(artifact.screenshotPath)) {
      const stats = fs.statSync(artifact.screenshotPath);
      screenshotSummary = `Screenshot present: ${artifact.screenshotPath} (${stats.size} bytes)`;
      imagePrefix = fs.readFileSync(artifact.screenshotPath).toString('base64').slice(0, 1200);
    }

    return [
      'You are a QA analyst. Evaluate if the artifact satisfies the acceptance criterion.',
      'Return ONLY JSON with keys: status(pass/fail), confidence(0-1), reasoning, recommended_test_update.',
      '',
      `Criterion: ${criterion.statement}`,
      `Observed text: ${artifact.observedText}`,
      `DOM snapshot: ${artifact.domSnapshot.slice(0, 3000)}`,
      `Image summary: ${screenshotSummary}`,
      `Image(base64-prefix): ${imagePrefix}`
    ].join('\n');
  }

  async #postJson(url, payload) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      if (!resp.ok) {
        throw new Error(`Ollama request failed with status ${resp.status}`);
      }

      const parsed = await resp.json();
      return parsed.response || '{}';
    } catch (err) {
      throw new Error(`Failed to connect to Ollama at ${this.host}. Is 'ollama serve' running?`, { cause: err });
    } finally {
      clearTimeout(timeout);
    }
  }

  #parseModelOutput(text) {
    try {
      return JSON.parse(text);
    } catch {
      return {
        status: 'fail',
        confidence: 0,
        reasoning: `Model response was not valid JSON: ${text.slice(0, 200)}`,
        recommended_test_update: 'Retry with stricter prompt or fallback to mock backend.'
      };
    }
  }
}
