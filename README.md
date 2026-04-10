# Evaluating AI Agents: DeepEval, Inspect AI, and Azure AI Evaluation SDK

Professional, hands-on reference repository for evaluating AI agents across three complementary ecosystems:

- `DeepEval` for test-first and CI-friendly LLM/agent evaluation
- `Inspect AI` for structured task pipelines (`Dataset -> Solver -> Scorer`)
- `Azure AI Evaluation SDK` for Azure-native agentic metrics and batch evaluation

This repository is designed for workshops, technical talks, and practical experimentation with real evaluation patterns.

## Table of Contents

1. [Project Goals](#project-goals)
2. [What You Will Learn](#what-you-will-learn)
3. [Repository Structure](#repository-structure)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Environment Configuration](#environment-configuration)
7. [How to Run](#how-to-run)
8. [Script-by-Script Overview](#script-by-script-overview)
9. [Output and Logs](#output-and-logs)
10. [Documentation](#documentation)
11. [Troubleshooting](#troubleshooting)
12. [Recommended Workflow](#recommended-workflow)

## Project Goals

The project demonstrates a practical, multi-framework approach to agent evaluation:

- validate final answers and intermediate behavior
- evaluate tool-use quality and adherence to user tasks
- test safety-related behavior with explicit scoring heuristics
- run single-case and dataset-scale (batch) evaluations
- prepare evaluation patterns suitable for CI/CD and technical presentations

## What You Will Learn

By working through the scripts, you will learn how to:

- define reusable eval test cases and custom judge metrics
- instrument component-level traces (`@observe`) for white-box analysis
- build Inspect AI tasks using decorators (`@task`, `@tool`, `@scorer`)
- evaluate agent conversations with OpenAI-style message traces
- run Azure evaluator classes for intent, adherence, and tool-call quality
- scale evaluations using JSONL datasets and evaluator column mappings

## Repository Structure

```text
.
|-- 01_deepeval_agent_eval.py
|-- 02_inspect_ai_agent_eval.py
|-- 03_azure_ai_eval_agents.py
|-- requirements.txt
|-- test_deepeval_agent_eval.py
|-- docs/
|   |-- guide_en.md
|   |-- guide_es.md
|   |-- technical_guide_en.md
|   `-- technical_guide_es.md
|-- logs/
`-- archive/
```

Notes:

- `logs/` stores Inspect AI evaluation logs (`.eval`) for review in `inspect view`.
- `archive/` contains older exploratory scripts kept for reference.

## Prerequisites

- Python `3.10+` recommended
- Access to model providers used by each framework
- API credentials depending on the script you run

## Installation

### Option A: Using virtual environment (recommended)

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Bash (macOS/Linux):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option B: Existing environment

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the repository root when running Azure examples.

```env
# Azure AI Evaluation SDK
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_KEY=your-azure-openai-key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-12-01-preview
```

Additional environment variables:

- DeepEval: `OPENAI_API_KEY` (or alternative model provider setup)
- Inspect AI: `INSPECT_EVAL_MODEL` (example: `openai/gpt-4o`)

## How to Run

### 1) DeepEval examples

```bash
python 01_deepeval_agent_eval.py
```

CI-style execution:

```bash
deepeval test run 01_deepeval_agent_eval.py
```

### 2) Inspect AI tasks

Run all tasks:

```bash
inspect eval 02_inspect_ai_agent_eval.py
```

Run one task:

```bash
inspect eval 02_inspect_ai_agent_eval.py@customer_support_agent
inspect eval 02_inspect_ai_agent_eval.py@travel_planning_agent
inspect eval 02_inspect_ai_agent_eval.py@react_agent_eval
inspect eval 02_inspect_ai_agent_eval.py@safety_evaluation
```

View logs in browser UI:

```bash
inspect view
```

### 3) Azure AI Evaluation SDK examples

```bash
python 03_azure_ai_eval_agents.py
```

If `AZURE_API_KEY` is not set, the script prints setup guidance and skips live API calls.

## Script-by-Script Overview

### `01_deepeval_agent_eval.py`

Main sections:

- end-to-end black-box evaluation with `GEval` + built-in metrics
- tool correctness validation with expected vs actual tool calls
- component-level tracing using `@observe` and `update_current_span(...)`
- custom edge-case metric definition
- pytest-compatible CI tests with `assert_test(...)`

Best for:

- rapid developer iteration
- regression checks in CI/CD
- combining black-box and white-box evaluation styles

### `02_inspect_ai_agent_eval.py`

Main sections:

- custom tools via `@tool`
- executable tasks via `@task`
- custom safety scorer via `@scorer(metrics=[accuracy()])`
- multi-task coverage (support, travel planning, ReAct behavior, safety)

Best for:

- structured benchmark-like evaluation workflows
- rich task composition and reproducible execution
- log-driven analysis using Inspect viewer

### `03_azure_ai_eval_agents.py`

Main sections:

- `IntentResolutionEvaluator`
- `TaskAdherenceEvaluator`
- `ToolCallAccuracyEvaluator`
- OpenAI-style message-trace inputs
- batch evaluation via `evaluate(...)` over JSONL
- quality + safety guidance section

Best for:

- Azure-native evaluation pipelines
- agentic metrics tied to production model deployments
- batch scoring and evaluator-specific column mapping

## Output and Logs

- Inspect AI writes run artifacts to `logs/`.
- Azure batch example writes temporary JSONL to the OS temp directory and removes it after execution.
- DeepEval results are printed to console and can be integrated with pytest/deepeval test pipelines.

## Documentation

Presentation and deep-dive documentation is available under `docs/`:

- `docs/guide_en.md`: speaker guide (EN)
- `docs/guide_es.md`: speaker guide (ES)
- `docs/technical_guide_en.md`: detailed technical walkthrough (EN)
- `docs/technical_guide_es.md`: detailed technical walkthrough (ES)
- `docs/integration_checklist_en.md`: real-agent integration go-live checklist (EN)
- `docs/integration_checklist_es.md`: real-agent integration go-live checklist (ES)

## Troubleshooting

### DeepEval issues

- ensure `OPENAI_API_KEY` (or your configured model provider) is available
- some metrics are model-judge dependent and can vary slightly run-to-run

### Inspect AI issues

- set `INSPECT_EVAL_MODEL` or pass `--model`
- confirm provider credentials are configured for your selected model backend
- run `inspect view` after successful eval runs to inspect traces

### Azure AI Evaluation SDK issues

- verify `.env` values (`AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME`, `AZURE_API_VERSION`)
- use a chat-capable deployment (`gpt-4o`, `gpt-4.1-mini`, etc.)
- ensure tool-call content includes `tool_call_id` where required
- note that `TaskAdherenceEvaluator` behavior can vary by SDK version (binary-like output observed in this repository)

## Recommended Workflow

1. Start with `01_deepeval_agent_eval.py` for fast local quality checks.
2. Use `02_inspect_ai_agent_eval.py` to validate richer multi-step agent behavior.
3. Run `03_azure_ai_eval_agents.py` for Azure-aligned agentic metrics and batch evaluation patterns.
4. Use `docs/technical_guide_en.md` or `docs/technical_guide_es.md` for presentation-ready explanations.

---

