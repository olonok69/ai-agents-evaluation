# Agentic AI Evaluation Technical Guide (EN)

This guide documents the codebase implementation for:

- `01_deepeval_agent_eval.py`
- `02_inspect_ai_agent_eval.py`
- `03_azure_ai_eval_agents.py`

It focuses on three things:

1. Core concepts behind agent evaluation.
2. How each library maps those concepts to concrete APIs.
3. How each script is structured and why each section exists.

---

## 1. Conceptual Baseline: What You Are Evaluating

Agent evaluation is different from single-turn LLM evaluation because quality is not only about final output text.

For agents, you usually evaluate across these dimensions:

- `intent understanding`: Did the agent understand the user goal?
- `task completion/adherence`: Did it actually satisfy the request?
- `tool behavior`: Did it call the right tools with the right args and sequence?
- `response quality`: Relevance, coherence, fluency, factuality.
- `safety`: Harmful content, prompt injection, policy violations.
- `operational behavior`: Reliability, latency, cost, regressions across versions.

The three scripts intentionally cover different levels of this stack:

- `DeepEval`: test-first and CI style, pytest-like developer workflow.
- `Inspect AI`: evaluation task framework (Dataset -> Solver -> Scorer) with agent/tool emphasis.
- `Azure AI Evaluation SDK`: evaluator-centric quality/safety APIs, including agentic metrics and batch `evaluate()`.

---

## 2. Environment and Setup

From workspace root:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently maps to:

- `deepeval>=3.0.0`
- `inspect-ai>=0.3.130`
- `azure-ai-evaluation>=1.0.0`
- `azure-identity>=1.15.0`
- `python-dotenv>=1.0.0`

Recommended env vars by script:

- DeepEval: `OPENAI_API_KEY` (or custom model provider config).
- Inspect: provider key + `INSPECT_EVAL_MODEL`.
- Azure SDK: `AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME`, `AZURE_API_VERSION`.

---

## 3. `01_deepeval_agent_eval.py` Detailed Code Walkthrough

## 3.1 Purpose and Design

This script demonstrates both:

- black-box evaluation (`evaluate(...)`) for final outputs.
- component-level tracing (`@observe`) for internal agent behavior.

It also includes CI-ready tests at the bottom, showing how to gate merges on eval metrics.

## 3.2 Key Imports and Their Roles

- `deepeval.evaluate`: bulk execution without pytest.
- `GEval`: LLM-as-judge custom metric builder.
- `ToolCorrectnessMetric`, `AnswerRelevancyMetric`, `PlanQualityMetric`, `PlanAdherenceMetric`: built-in metrics.
- `LLMTestCase`, `ToolCall`: test data schema.
- `observe`, `update_current_span`: tracing and per-span test-case binding.
- `assert_test`: pytest assertion integration.

## 3.2.1 Decorators, Classes, and Methods You Should Explain

### Decorator: `@observe(...)`

What it does:

- wraps a function call in a trace span that DeepEval can evaluate.
- attaches metadata (for example operation type such as `agent` or `tool`).

Why it matters when presenting:

- it gives you visibility into intermediate steps, not only final output.
- you can explain failures at the exact stage where quality degraded.

How to describe runtime behavior:

- when the decorated function starts, a span is opened.
- inside the function, `update_current_span(...)` can attach test-case data.
- when the function returns, the span closes and metrics can be applied.

### Method: `update_current_span(...)`

What it does:

- binds an `LLMTestCase` to the currently active trace span.
- provides evaluator context for that specific step.

Practical teaching point:

- this is the bridge between business logic execution and evaluation logic.

### Class: `LLMTestCase`

Role:

- canonical data container for one evaluation item.
- holds fields such as `input`, `actual_output`, `expected_output`, and optional tool-call fields.

Teaching angle:

- treat it like a test vector for LLM/agent behavior.

### Class: `GEval`

Role:

- configurable LLM-as-judge metric.
- combines name, criteria, and scoring parameters into one reusable metric object.

Teaching angle:

- this is where domain rubric lives (for example "is this escalation decision policy-compliant?").

### Method: `evaluate(...)`

Role:

- executes one or many metrics against one or many test cases.

Teaching angle:

- use it when you want script-driven eval runs (outside pytest).

### Method: `assert_test(...)`

Role:

- pytest-friendly assertion wrapper for metric outcomes.

Teaching angle:

- converts eval expectations into CI gates.

## 3.3 Section-by-Section

### Example 1: End-to-End Black-Box

Function: `example_1_end_to_end_evaluation()`

What it shows:

- building a custom judge metric (`GEval`) with explicit criteria.
- combining custom and built-in metrics.
- evaluating multiple `LLMTestCase` items in one call.

Why this matters:

- it gives a practical regression signal for user-visible behavior.
- it does not require instrumenting internal code paths.

### Example 2: Tool Correctness

Function: `example_2_tool_correctness()`

What it shows:

- explicit `tools_called` vs `expected_tools`.
- checking agent-tool alignment independent of prose quality.

Why this matters:

- catches silent failures where output looks plausible but tool use is wrong.

### Example 3: Component-Level Tracing

Function: `example_3_component_level_tracing()`

What it shows:

- tracing an orchestrated agent path (`travel_agent` -> reasoning -> tools).
- attaching different metrics to different levels.
- populating runtime span test-case via `update_current_span(...)`.

Why this matters:

- best fit for debugging where failure happened (plan vs tool vs final output).

### Example 4: Custom Edge-Case Metric

Function: `example_4_custom_geval_metric()`

What it shows:

- defining domain-specific quality rubric with `GEval`.
- validating ambiguous requests and clarification behavior.

Why this matters:

- generic metrics are rarely enough for production agent behavior.

### Section 5: CI Tests

Functions:

- `test_agent_tool_selection()`
- `test_agent_response_quality()`

What it shows:

- `assert_test` as a CI gate.
- deterministic structure for pipeline usage.

Important note:

- these tests are model/provider dependent and can fail without proper judge model config.

## 3.4 When to Use This Script Pattern

Use this pattern when:

- you want fast local iteration with pytest semantics.
- you need custom rubrics and developer-first regression checks.
- you want both black-box and white-box eval modes.

## 3.5 Two-Minute Speaking Script (DeepEval)

"In this file, the key idea is that evaluation is treated like testing. I start with `LLMTestCase`, which is the data contract for what I expect from the agent. Then I combine metrics, including custom `GEval` rubrics and built-in tool or quality metrics.

The most important decorator here is `@observe`. It wraps functions in trace spans so I can evaluate not only final output but also intermediate behavior. Inside those spans, `update_current_span(...)` binds runtime data to the current step. That is what gives me debugging visibility when an agent fails for the right answer but wrong process.

Finally, I use `evaluate(...)` for script-style runs and `assert_test(...)` for CI gating. So conceptually: this script is a developer workflow for rapid regression checks and merge protection." 

---

## 4. `02_inspect_ai_agent_eval.py` Detailed Code Walkthrough

## 4.1 Purpose and Design

This script demonstrates Inspect AI task composition for agent evaluations.

Core abstraction:

- `Task = Dataset + Solver + Scorer`

This is useful for benchmark-like reproducible tasks and flexible solver pipelines.

## 4.2 Key Imports and Roles

- `@task`, `Task`: register runnable eval tasks.
- `Sample`: dataset row.
- `generate`, `system_message`, `use_tools`: solver pipeline primitives.
- `@tool`: custom async tool wrappers.
- scorers: `model_graded_fact`, `accuracy`, plus custom scorer API.
- `react`: built-in ReAct agent loop.

## 4.2.1 Decorators, Classes, and Methods You Should Explain

### Decorator: `@tool`

What it does:

- registers a Python function as a callable tool in Inspect.
- expects you to return an async `execute(...)` function that is invoked at runtime.

Why this pattern exists:

- separates tool declaration from execution implementation.
- allows Inspect to expose tool signatures/descriptions to the model.

Presentation tip:

- call out that docstrings and type hints improve tool-use quality because they become part of the model-facing tool contract.

### Decorator: `@task`

What it does:

- marks a function returning `Task(...)` as a runnable eval task.
- enables CLI addressing like `file.py@task_name`.

Presentation tip:

- this is the main unit of evaluation packaging in Inspect.

### Decorator: `@scorer(metrics=[...])`

What it does:

- declares a custom scoring function and wires metric aggregation metadata.
- in this script, `refusal_scorer` returns `CORRECT` or `INCORRECT` plus explanation.

Presentation tip:

- this is where policy checks become explicit and auditable.

### Class: `Task`

Role:

- top-level container for `dataset`, `solver`, and `scorer`.

How to explain it quickly:

- "Task is the executable contract: what to run, how to run it, and how to score it."

### Class: `Sample`

Role:

- one dataset row (`input` prompt + `target` expectation).

Presentation tip:

- targets can be strict answers or looser expected facts depending on scorer strategy.

### Solver methods: `system_message(...)`, `use_tools(...)`, `generate()`

Execution order:

1. `system_message(...)` sets model behavior constraints.
2. `use_tools(...)` attaches tool interfaces available to the model.
3. `generate()` runs model completion for the sample.

Teaching angle:

- this explicit chain makes orchestration behavior easy to inspect and compare across runs.

### ReAct solver: `react(...)`

Role:

- enables iterative reason/act cycles with tools.
- supports harder tasks where one-shot completion is insufficient.

Safety/ops note:

- `message_limit` is a practical guardrail to prevent runaway loops.

### Scoring types: `Score`, `Target`, `CORRECT`, `INCORRECT`

Role:

- standardized output contract for custom scorers.

Presentation tip:

- returning an `explanation` string is as important as the label, because it speeds up debugging and model iteration.

## 4.3 Section-by-Section

### Tool Definitions (`search_knowledge_base`, `calculate_shipping`, etc.)

What it shows:

- custom tools as async functions with clear signatures.
- deterministic mock data for reproducible evaluation behavior.

Why this matters:

- tool behavior is explicit and stable for testing.

### Task 1: `customer_support_agent`

What it shows:

- standard QA/support task with tool use.
- model-graded scoring over expected target intent/facts.

### Task 2: `travel_planning_agent`

What it shows:

- multi-tool composition in a single request.
- richer synthesis requirements than one-shot QA.

### Task 3: `react_agent_eval`

What it shows:

- ReAct-style agent loop with `message_limit` guard.
- closer to autonomous multi-step behavior.

### Task 4: `safety_evaluation` + `refusal_scorer`

What it shows:

- policy behavior checks for harmful prompts.
- custom scorer with explicit refusal heuristic and binary outcome.

## 4.4 Runtime Model

Primary run path is CLI:

```bash
inspect eval 02_inspect_ai_agent_eval.py
```

You can run all tasks or target one task:

```bash
inspect eval 02_inspect_ai_agent_eval.py@customer_support_agent
```

Inspect logs are emitted under `./logs/` and viewable via:

```bash
inspect view
```

## 4.5 When to Use This Script Pattern

Use this pattern when:

- you need strong evaluation task modeling (datasets/solvers/scorers).
- you want benchmark-like workflows and detailed execution logs.
- you need agent and tool behavior with reproducible orchestrations.

## 4.6 Two-Minute Speaking Script (Inspect AI)

"This file is organized around Inspect's core abstraction: `Task = Dataset + Solver + Scorer`. A `Sample` gives one input-target row, the solver defines how the model runs, and the scorer defines how quality is judged.

The decorators are central. `@task` registers runnable task units for CLI execution. `@tool` turns Python functions into model-callable tools, where type hints and docstrings become part of the tool contract. `@scorer` defines a custom grading function, which is how I make safety policies explicit, like refusal checks.

For execution flow, read solver chains top-down: `system_message(...)`, `use_tools(...)`, then `generate()`. For harder cases, `react(...)` introduces iterative reason-act cycles. So this script is best understood as a reproducible benchmark pipeline with clear separation of data, orchestration, and scoring." 

---

## 5. `03_azure_ai_eval_agents.py` Detailed Code Walkthrough

## 5.1 Purpose and Design

This script demonstrates Azure AI Evaluation SDK agentic metrics with both:

- single-run evaluator calls.
- batch `evaluate(...)` over JSONL.

Primary evaluators:

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`

## 5.2 Configuration

`AzureOpenAIModelConfiguration` is used as the model config object:

- `azure_endpoint`
- `api_key`
- `azure_deployment`
- `api_version`

This script uses env names:

- `AZURE_ENDPOINT`
- `AZURE_API_KEY`
- `AZURE_DEPLOYMENT_NAME`
- `AZURE_API_VERSION`

## 5.2.1 Decorators, Classes, and Methods You Should Explain

This script is evaluator-oriented and does not rely on Python decorators.
The important teaching focus is class-based evaluator invocation.

### Class: `AzureOpenAIModelConfiguration`

Role:

- encapsulates model endpoint/deployment/auth settings.
- passed into evaluators so scoring calls use a consistent model configuration.

Presentation tip:

- explain this as dependency injection for the judge model.

### Evaluator classes

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`

Shared runtime pattern:

- instantiate evaluator with `model_config` (or with explicit evaluator settings).
- call evaluator like a function: `result = evaluator(query=..., response=...)`.

Teaching angle:

- these objects are callable evaluators; each returns a structured dictionary with score keys and optional reason fields.

### Method: evaluator `__call__(...)`

Practical behavior:

- validates input schema.
- runs evaluator prompt/inference path.
- returns normalized metric outputs.

Presentation tip:

- this is why input shape quality (especially message traces and tool-call IDs) directly affects reliability.

### Function: `evaluate(...)` (batch mode)

Role:

- executes one or many evaluators over a JSONL dataset.
- supports per-evaluator `column_mapping` so different evaluators can read different fields.

Teaching angle:

- it is the production-friendly path for nightly or release-candidate evaluation jobs.

## 5.3 Critical Input Schema Notes

Based on current SDK behavior and docs:

- Tool calls must include `tool_call_id` for tool-call content items.
- Agent message format should follow OpenAI-style message lists.
- For evaluator parsing reliability, user/assistant message `content` is represented as list-of-items objects (`type: text/tool_call/tool_result`) in this script.

## 5.4 Section-by-Section

### Example 1: Intent Resolution

Function: `example_1_intent_resolution()`

What it shows:

- clear positive, negative, and clarification cases.
- pass/fail threshold interpretation for intent alignment.

### Example 2: Task Adherence

Function: `example_2_task_adherence()`

What it shows:

- positive case includes tool-call and tool-result evidence.
- negative case remains intentionally under-specified.
- reason fields are printed for explainability.

Important implementation detail:

- in currently installed SDK builds, task adherence output is binary-like (`1.0/0.0` + reason) even when older docs mention Likert style. Treat this as version-sensitive behavior.

### Example 3: Tool Call Accuracy

Function: `example_3_tool_call_accuracy()`

What it shows:

- explicit `tool_definitions` and `tool_calls` arrays.
- direct evaluation of procedural tool quality.

### Example 4: Message Trace Evaluation

Function: `example_4_agent_messages_format()`

What it shows:

- constructing evaluator-friendly `query_messages` and `response_messages` from a trace.
- evaluating intent and adherence on structured conversation data.

### Example 5: Batch Evaluation

Function: `example_5_batch_evaluation()`

What it shows:

- generating JSONL eval input.
- running multiple evaluators in one `evaluate(...)` call.
- `column_mapping` usage for different evaluator input shapes.

Operational note:

- warnings like `Aggregated metrics for evaluator is not a dictionary...` can appear from SDK batch internals and are often non-fatal when all lines complete.

### Example 6: Combined Quality + Safety (quality executed, safety described)

Function: `example_6_quality_and_safety()`

What it shows:

- running quality evaluators together.
- printing reason fields for intent/task.
- documenting safety evaluators and prerequisites.

Current script behavior:

- safety evaluators are not executed in this function; the script documents supported safety metrics and Foundry requirement.

## 5.5 When to Use This Script Pattern

Use this pattern when:

- you want direct access to Azure evaluator APIs.
- you need agentic metrics tied to tool behavior and intent/task outcomes.
- you want batch evaluation with optional Foundry integration.

## 5.6 Two-Minute Speaking Script (Azure AI Evaluation SDK)

"This script is evaluator-object driven. Instead of decorators, I instantiate evaluator classes such as `IntentResolutionEvaluator`, `TaskAdherenceEvaluator`, and `ToolCallAccuracyEvaluator` using `AzureOpenAIModelConfiguration`.

At runtime, each evaluator is callable, so I pass `query` and `response` (or message traces) and receive structured scores plus reason fields. The most important implementation detail is schema quality: tool-call IDs and message structure must be consistent, otherwise evaluator reliability drops.

For scale, I switch to batch `evaluate(...)` over JSONL and use per-evaluator `column_mapping` to feed the right fields to each metric. So this file is the production-oriented path: consistent evaluator contracts, explainable outputs, and batch-ready execution." 

---

## 6. Cross-Script Comparison

- `01_deepeval_agent_eval.py`: best for CI-style custom rubric testing and tracing in developer workflows.
- `02_inspect_ai_agent_eval.py`: best for structured eval tasks and benchmark-style execution pipelines.
- `03_azure_ai_eval_agents.py`: best for Azure-native evaluator APIs and agentic quality metrics.

A practical workflow is to combine them:

1. Use DeepEval in fast local/unit loops.
2. Use Inspect AI for scenario/benchmark suites and rich run logs.
3. Use Azure evaluators for production-aligned agentic quality tracking.

---

## 6.1 Presenter Cheat Sheet: How to Explain the Three Paradigms

If you need one sentence per script during a talk:

- `01_deepeval_agent_eval.py`: "Decorator-driven tracing and metric assertions for developer-first CI loops."
- `02_inspect_ai_agent_eval.py`: "Task objects with explicit dataset/solver/scorer composition for reproducible agent benchmarking."
- `03_azure_ai_eval_agents.py`: "Class-based evaluator calls and batch pipelines for Azure-native agentic quality tracking."

If you need one sentence per programming style:

- Decorator style: "Behavior is attached to functions declaratively (`@observe`, `@task`, `@tool`, `@scorer`)."
- Object style: "Behavior is attached to evaluator instances and invoked via callable classes."
- Pipeline style: "Behavior is attached to ordered solver steps and batch evaluators with mapping."

---

## 7. Integrating With a Real Agent (From Mock Data to Production Traces)

The examples in this repository use mock inputs to teach evaluator behavior.
In real projects, you should feed evaluators with actual agent traces.

At minimum, capture these fields from each run:

- `input`: what the user asked.
- `output`: final assistant response.
- `tool_calls`: tool name, arguments, result, and `tool_call_id` when available.

Recommended additional fields:

- `expected_output`: gold label or expected fact set.
- `expected_tools`: expected tool names for the scenario.
- metadata: `run_id`, model version, latency, timestamp, environment.

### 7.1 What to Replace in `01_deepeval_agent_eval.py`

Replace mock `LLMTestCase(...)` definitions with test cases generated from real logs.

Mapping:

- `input` <- real user prompt.
- `actual_output` <- final agent answer.
- `expected_output` <- gold answer/rubric target.
- `tools_called` <- tool calls from runtime trace.
- `expected_tools` <- expected tools from test scenario.

In `example_3_component_level_tracing()`, replace simulated functions with wrappers around your real orchestrator/tools so `@observe` spans represent true execution.

### 7.2 What to Replace in `02_inspect_ai_agent_eval.py`

Use one of two integration modes:

1. Harness mode:
	 Inspect runs your real agent for each `Sample`.
2. Replay mode:
	 Inspect scores outputs already captured in logs.

Concrete replacements:

- Replace mock `@tool` implementations with real connectors (API/database/service).
- Replace static `dataset=[Sample(...)]` with your eval scenarios.
- Keep `@task` and scorer structure, but route generation/tool execution through your real stack.

### 7.3 What to Replace in `03_azure_ai_eval_agents.py`

This script is already close to production integration.

Concrete replacements:

- Replace inline `query`/`response` examples with data built from real sessions.
- Build `query_messages`/`response_messages` from actual conversation traces.
- In batch mode (`example_5_batch_evaluation()`), write JSONL from real runs instead of static examples.

Critical schema requirement:

- include `tool_call_id` consistently in tool-call related message items.

### 7.4 Canonical Trace Schema (Recommended)

Use one normalized schema and transform it per framework.

```json
{
	"run_id": "abc-123",
	"timestamp": "2026-04-06T10:00:00Z",
	"input": "User request text",
	"output": "Final assistant response",
	"tool_calls": [
		{
			"tool_call_id": "call_001",
			"name": "search_flights",
			"arguments": {"origin": "NYC", "destination": "LON"},
			"result": [{"airline": "X", "price": 500}]
		}
	],
	"expected_output": "Optional gold answer",
	"expected_tools": ["search_flights"]
}
```

### 7.5 Suggested Rollout for Real Use Cases

1. Instrument your agent runtime once to capture normalized traces.
2. Export traces to JSON/JSONL.
3. Build adapters:
	 - trace -> DeepEval `LLMTestCase`
	 - trace -> Inspect `Sample`/task input
	 - trace -> Azure `query_messages`/`response_messages`
4. Run periodic evals (CI and/or nightly).
5. Track regressions and gate releases on metric thresholds.

### 7.6 Go-Live Checklist Companion

Use these checklists as an operational companion to this section:

- `docs/integration_checklist_en.md`
- `docs/integration_checklist_es.md`

## 8. References

- DeepEval docs: https://deepeval.com/docs/getting-started?utm_source=GitHub
- DeepEval repo: https://github.com/confident-ai/deepeval
- Inspect docs: https://inspect.aisi.org.uk/
- Inspect repo: https://github.com/UKGovernmentBEIS/inspect_ai?tab=readme-ov-file
- Azure agentic metrics blog: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/evaluating-agentic-ai-systems-a-deep-dive-into-agentic-metrics/4403923
- Azure AI Evaluation SDK repo: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation
- Azure Foundry classic agent evaluate docs: https://learn.microsoft.com/en-us/azure/foundry-classic/how-to/develop/agent-evaluate-sdk
