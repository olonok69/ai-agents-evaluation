# Real Agent Evaluation Integration Checklist (EN)

Use this checklist before promoting agent changes to staging/production.

## 1) Data Capture Readiness

- [ ] Each agent run captures `run_id`, `timestamp`, `input`, `output`.
- [ ] Tool traces are captured with `name`, `arguments`, `result`.
- [ ] Tool calls include stable `tool_call_id` when available.
- [ ] Model/deployment metadata is captured (model name, version, environment).
- [ ] Latency and token/cost metadata is captured for operations analysis.

## 2) Canonical Trace Schema

- [ ] A normalized JSON schema is defined and versioned.
- [ ] Optional labels are supported: `expected_output`, `expected_tools`.
- [ ] Schema validation exists (JSON Schema, pydantic, or equivalent).
- [ ] Missing/invalid trace fields are logged with explicit errors.

## 3) Framework Adapters

- [ ] Adapter exists: trace -> DeepEval `LLMTestCase`.
- [ ] Adapter exists: trace -> Inspect `Sample` / task input.
- [ ] Adapter exists: trace -> Azure `query_messages` / `response_messages`.
- [ ] Azure adapter preserves message structure and `tool_call_id` consistency.
- [ ] Batch export to JSONL is deterministic and reproducible.

## 4) DeepEval Integration

- [ ] Core metrics selected (for example `GEval`, `AnswerRelevancyMetric`, `ToolCorrectnessMetric`).
- [ ] Thresholds are defined and documented per metric.
- [ ] CI command is wired (for example `deepeval test run ...`).
- [ ] Flaky tests are identified and handled with reruns or tighter rubrics.

## 5) Inspect AI Integration

- [ ] Task boundaries are explicit (`@task` per scenario family).
- [ ] Dataset reflects real user intents and failure modes.
- [ ] Tool implementations are production-like or clearly mocked.
- [ ] Custom scorers return both label and explanation.
- [ ] Logs are reviewed with `inspect view` after each evaluation cycle.

## 6) Azure AI Evaluation SDK Integration

- [ ] `AzureOpenAIModelConfiguration` uses correct endpoint, key, deployment, API version.
- [ ] `IntentResolutionEvaluator`, `TaskAdherenceEvaluator`, and `ToolCallAccuracyEvaluator` are mapped to the right inputs.
- [ ] Batch `evaluate(...)` uses per-evaluator `column_mapping` correctly.
- [ ] Known SDK warning paths are documented for your team.
- [ ] Version-sensitive evaluator behavior is tracked in release notes.

## 7) Quality and Safety Coverage

- [ ] Positive and negative test cases are both present.
- [ ] Safety scenarios are included (prompt injection, policy bypass attempts, harmful requests).
- [ ] Refusal behavior is tested with explicit policy criteria.
- [ ] Human review is scheduled for calibration of automated judges.

## 8) CI/CD and Release Gates

- [ ] Baseline metrics are stored and versioned.
- [ ] Regression thresholds are defined per metric.
- [ ] Pipeline fails on critical regressions.
- [ ] Evaluation artifacts are archived per build/release.
- [ ] Rollback criteria are documented.

## 9) Operations and Monitoring

- [ ] Nightly or scheduled eval runs are configured.
- [ ] Trend dashboard tracks metric drift over time.
- [ ] Alerting exists for significant score drops.
- [ ] Cost and latency are monitored with quality metrics.

## 10) Final Go-Live Decision

- [ ] No critical metric is below release threshold.
- [ ] No unresolved blocking safety findings.
- [ ] Last human calibration review is approved.
- [ ] Release owner sign-off is recorded.

---

## Minimal Launch Set (if you need to start small)

1. Capture normalized traces for every run.
2. Run DeepEval + Azure intent/task/tool metrics nightly.
3. Add one Inspect task suite for top 10 user journeys.
4. Gate releases on 2-3 critical metrics.
5. Review failing traces weekly with engineering + product.
