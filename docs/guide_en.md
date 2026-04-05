# EVALUATING AI AGENTS
## Techniques, Tools & Frameworks

**Speaker Guide — 60-Minute Technical Presentation**

---

**Juan Salvador Huertas Romero**
Senior AI/ML Engineer

*A Practitioner's Guide for 2025–2026*

---

## Session Overview

This guide accompanies a 15-slide presentation designed for a technical audience already familiar with generative AI, LLMs, and agent architectures. The goal is not to introduce what agents are, but to provide a structured, actionable framework for evaluating them — from development through production.

### Related Technical Guides

- Deep technical code walkthrough (EN): `docs/technical_guide_en.md`
- Conceptual technical summary (ES): `docs/technical_guide_es.md`

### Timing Breakdown

| Time | Section | Slides | Duration |
|------|---------|--------|----------|
| 0:00 | Opening & Why Agent Evals Differ | 1–3 | 8 min |
| 0:08 | 7 Core Evaluation Techniques | 4–5 | 10 min |
| 0:18 | Metrics That Matter | 6 | 7 min |
| 0:25 | Benchmarks & Frameworks | 7–8 | 8 min |
| 0:33 | Production Tooling | 9 | 5 min |
| 0:38 | Hands-On Code Examples (DeepEval, Inspect AI, Azure) | 10–12 | 12 min |
| 0:50 | Best Practices & Key Takeaways | 13–15 | 5 min |
| 0:55 | Q&A | — | 5 min |

---

## ⏱ 0:00 – 0:08 — Opening & Why Agent Evals Differ (Slides 1–3)

### Opening Hook

Start with a provocative data point: according to the LangChain 2026 State of Agent Engineering report, 57% of organizations now run agents in production, yet quality remains the number-one barrier — cited by 32% of teams. Even more striking: while 89% have observability, only 52% have implemented evals. This gap between "we can see what our agents do" and "we can measure whether they do it well" is the core problem this talk addresses.

> 💡 **Speaker Note:** Open with energy. This stat usually gets heads nodding — most people in the room will recognize this gap in their own organizations. Pause after the 52% stat to let it land.

### Why Agents Break Traditional Evals

Agents fail in fundamentally different ways than standard LLM applications. Walk through four key differences:

**Non-determinism:** The same input produces different action sequences on each run. A flight-booking agent might search by price first on one run and by schedule first on another — both reaching correct results through different paths. This makes simple input/output comparison insufficient.

**Multi-step reasoning:** You need to evaluate the entire trajectory (the chain of reasoning, tool calls, and decisions), not just the final answer. An agent might produce the right answer via a flawed process — and that flawed process will eventually cause failures on harder tasks.

**Tool orchestration:** Agents select tools, pass arguments, interpret results, and decide what to do next. Each of these steps is a potential failure point. An agent might pick the right API but pass the wrong parameters, or call the right sequence of tools but in an inefficient order.

**Compound failures:** Errors cascade. A wrong tool selection leads to incorrect data, which leads to a flawed plan, which leads to a bad final output. Evaluating only the output misses the root cause.

> 💡 **Speaker Note:** Use the analogy: "Traditional LLM eval is like grading a math exam by checking the final answer. Agent eval is like grading the entire proof — did they use the right theorems, in the right order, with correct reasoning?"

---

## ⏱ 0:08 – 0:18 — 7 Core Evaluation Techniques (Slides 4–5)

Walk through each technique, emphasizing when to use it and its limitations. Don't spend equal time on all seven — focus on LLM-as-judge, trajectory evaluation, and tool-use evaluation, which are the most agent-specific.

### 1. LLM-as-Judge

The dominant method for evaluating open-ended agent outputs. A separate LLM grades agent responses against structured rubrics. Anthropic's January 2026 guidance recommends isolating each evaluation dimension into a separate judge call — don't ask one prompt to score correctness, completeness, and tone simultaneously. OpenAI's research shows automated graders achieve roughly 66% agreement with human experts, compared to 71% human inter-rater agreement. Close, but not equivalent — which is why you always need to track correlation between your model judge and periodic human evaluation.

### 2. Human Evaluation

Remains the gold standard for calibration. Hamel Husain recommends a "benevolent dictator" model: one domain expert who deeply understands users makes final quality decisions. Use human evaluation to calibrate your LLM judges, not as continuous monitoring — it doesn't scale. Reserve systematic human review for when you're establishing a new evaluation dimension or when your LLM judge scores don't match your intuition from reading transcripts.

### 3. Automated Benchmarks

Provide reproducible capability measurement. Mention the key static benchmarks (SWE-bench for coding, GAIA for tool-use reasoning, WebArena for browser automation) and highlight the emerging dynamic benchmarks: Anthropic's Bloom auto-generates behavioral evaluations from researcher-specified traits, preventing benchmark saturation.

### 4. Trajectory Evaluation

Assesses the complete reasoning and action chain, not just the final output. LangChain's AgentEvals library offers trajectory match evaluators with four strictness modes: strict (exact match), tool-call-only, ordered-subset, and unordered-subset. A critical insight from Anthropic: "Grade what the agent produced, not the path it took." Over-constraining the expected path penalizes creative but correct solutions.

### 5. Task Completion Metrics

Two metrics deserve attention. **pass@k** measures the probability that at least one of k independent trials succeeds — use this when one good answer suffices (like code generation). **pass^k** measures the probability that ALL k trials succeed — use this for customer-facing reliability where every interaction matters. At a per-trial 75% success rate with k=3, pass@k is 98% but pass^k drops to just 42%.

> 💡 **Speaker Note:** The pass@k vs pass^k distinction often generates 'aha' moments. Draw it out: 75% sounds great, but if you need reliability, you need pass^k, and that tells a very different story.

### 6. Multi-Turn Conversation Evaluation

Tests coherence, context retention, and goal tracking across exchanges. The standard approach uses a simulated user — a second LLM playing a user persona — which allows scalable testing of multi-turn interactions without humans in the loop.

### 7. Tool-Use Evaluation

Checks correct tool selection, parameter accuracy, calling efficiency, error handling, and sequence correctness. The Berkeley Function Calling Leaderboard (BFCL) provides standardized measurement. Highlight Amazon's discovery: poorly defined tool schemas cause cascading agent failures — they built an LLM-powered system to auto-generate standardized schemas across thousands of internal APIs.

---

## ⏱ 0:18 – 0:25 — Metrics That Matter (Slide 6)

Present the four-tier metrics stack. The key message: you need metrics at every layer, not just correctness.

### Correctness Tier (Measure Always)

Task success rate is the single most important metric. Industry benchmarks show world-class customer support agents reach 85–90% first-contact resolution. Combine with answer correctness (exact match or LLM-judged) and faithfulness (proportion of claims supported by source context) for RAG-based agents. Track hallucination rate as the inverse of faithfulness.

### Agent-Specific Tier (Critical for Debugging)

Tool call accuracy splits into selection accuracy (right tool?) and argument correctness (right parameters?). The Azure AI Evaluation SDK treats these as primary agentic metrics. Step efficiency — the ratio of optimal steps to actual steps — reveals agents that "spin" making redundant calls, wasting cost and time. Error recovery rate measures how effectively agents handle API failures and unexpected inputs.

### Performance Tier (Measure in Production)

Track latency at P50, P95, and P99 for end-to-end and per-step. Calculate cost per task as the sum of all LLM calls' token costs. Token efficiency (tasks completed per total tokens) reveals optimization opportunities — small inefficiencies compound across thousands of daily interactions.

### Safety Tier (Critical for User-Facing Agents)

Highlight the sobering finding from October 2025: all 12 published jailbreak defenses were bypassed at greater than 90% rates under adaptive attacks. Multi-turn attacks achieved 92% success rates across eight open-weight models. This makes multi-turn resilience a separate, essential metric from single-turn jailbreak resistance.

> 💡 **Speaker Note:** The safety stats tend to surprise even experienced ML engineers. Let that sink in — it reinforces why evaluation isn't optional, it's critical infrastructure.

---

## ⏱ 0:25 – 0:33 — Benchmarks & Frameworks (Slides 7–8)

Walk through the benchmarks table briefly — don't read every row. Focus on three or four that are most relevant to the audience. Then dive into the five frameworks.

### Inspect AI (UK AI Security Institute)

The most complete open-source evaluation framework for rigorous teams. Its power lies in the composable primitive model: Dataset feeds into Task, which chains Solvers (prompt engineering, tool use, ReAct agents), and outputs are checked by Scorers. Sandboxed execution via Docker or Kubernetes ensures safe agent evaluation. Over 100 pre-built evaluations can be run with a single command. Adopted by Anthropic, DeepMind, and other frontier labs. MIT licensed, actively maintained with 50+ contributors.

### DeepEval (Confident AI)

Think of it as "Pytest for LLM apps." Its strength is developer ergonomics: native pytest integration makes adding eval gates to CI/CD trivial. Offers 50+ research-backed metrics including six agent-specific ones: TaskCompletion, ToolCorrectness, ArgumentCorrectness, StepEfficiency, PlanQuality, and PlanAdherence. The `@observe` decorator traces agent internals without rewriting your codebase. The v3.0 DAG metric introduced deterministic LLM-as-judge using decision trees for more consistent scoring.

### Azure AI Evaluation SDK (Microsoft)

Three purpose-built agentic evaluators: **IntentResolutionEvaluator** (did the agent understand the user's goal?), **TaskAdherenceEvaluator** (did the response satisfy the request?), and **ToolCallAccuracyEvaluator** (were tool calls correct and efficient?). Native integration with Azure AI Foundry Agent Service via a converter that transforms agent threads into evaluation-ready data. Best for teams already in the Azure ecosystem.

### Ragas & LangSmith

Ragas remains the standard for RAG evaluation (Context Precision, Context Recall, Faithfulness) and has expanded to include agent metrics. LangSmith provides the tightest integration for LangChain/LangGraph users with trajectory match evaluators and a new Insights Agent that automatically categorizes production behavior patterns.

---

## ⏱ 0:33 – 0:38 — Production Tooling (Slide 9)

Walk through the production tools table. The key message here is convergence on OpenTelemetry as the standard instrumentation layer. The GenAI Semantic Conventions (v1.37+) standardize prompt, response, token, and tool-call schemas. An Agent Framework Semantic Convention defining Tasks, Actions, Agents, Teams, and Memory is under active development with contributions from Amazon, Google, IBM, and Microsoft.

**LangSmith:** Most integrated for LangChain teams. Handles 1B+ traces. Free tier with 5k traces/month.

**Arize Phoenix:** Strongest open-source option. Self-hostable, OTel-native with 50+ auto-instrumentations.

**Braintrust:** Fastest CI/CD iteration loop with a dedicated GitHub Action. Loop AI generates domain-specific scorers from natural language descriptions.

**Galileo:** Sub-200ms evaluation latency using proprietary Luna-2 SLMs at roughly $0.02 per million tokens — enabling real-time guardrails economically.

**Patronus AI:** Research-grade evaluation with Lynx hallucination detector (outperforms GPT-4 by 8.3% on medical hallucination).

> 💡 **Speaker Note:** The OTel point is the strategic takeaway. Regardless of which tools you choose today, instrumenting with OTel-compatible telemetry prevents vendor lock-in. This resonates strongly with engineering leaders.

---

## ⏱ 0:38 – 0:50 — Hands-On Code Examples (Slides 10–12)

This is the most engaging section. Walk through each code example on screen, explaining the key patterns rather than reading code line by line. Encourage the audience to use the provided Python scripts for hands-on experimentation after the talk.

### DeepEval Example (Slide 10)

Explain the key patterns: the `@observe` decorator for non-intrusive tracing, how metrics are attached to specific components (not just the final output), and how `update_current_span` connects test case data to the traced execution. Highlight the six agent-specific metrics: ToolCorrectness, PlanQuality, PlanAdherence, TaskCompletion, ArgumentCorrectness, and StepEfficiency. The script (`01_deepeval_agent_eval.py`) contains five complete examples covering black-box evaluation, tool correctness, component-level tracing, custom G-Eval metrics, and pytest CI/CD integration.

### Inspect AI Example (Slide 11)

Emphasize the composable architecture: Dataset provides test cases, Solver chains define the evaluation pipeline (system message, tool use, generate), and Scorer evaluates the output. Show how `@tool` defines custom tools as simple Python async functions with docstrings that become the tool description for the LLM. The `react()` solver provides a ReAct loop with retry logic. The script (`02_inspect_ai_agent_eval.py`) includes four tasks: customer support, travel planning, ReAct agent, and safety evaluation with a custom refusal scorer.

### Azure AI Evaluation SDK Example (Slide 12)

Walk through the three agentic evaluators. IntentResolutionEvaluator and TaskAdherenceEvaluator output Likert scores (1–5), while ToolCallAccuracyEvaluator outputs a passing rate (0–1). Show the two input formats: simple strings (query + response) and full OpenAI-style message traces. Highlight the `evaluate()` function for batch evaluation with JSONL datasets, and the Azure AI Agent Converter for seamless integration with Foundry Agent Service. The script (`03_azure_ai_eval_agents.py`) contains six examples covering all three evaluators, message format, batch evaluation, and combined quality-safety assessment.

> 💡 **Speaker Note:** Don't try to run the code live unless you've tested the environment. Instead, walk through the patterns and point to the scripts for self-study. Offer to share the repository link at the end.

---

## ⏱ 0:50 – 0:55 — Best Practices & Key Takeaways (Slides 13–15)

### Best Practices to Emphasize

**1. Start with 20–50 tasks from real failures.** Anthropic's January 2026 guide emphasizes that early changes have large effect sizes, so small sample sizes suffice. Convert manual checks into automated test cases. A good task is one where two domain experts would independently reach the same pass/fail verdict.

**2. Three-level evaluation pyramid.** Hamel Husain's framework: Level 1 (code-based assertions) runs on every commit — cheap, fast, deterministic. Level 2 (LLM-as-judge) runs on a set cadence for subjective quality. Level 3 (human evaluation) runs only after significant product changes.

**3. Handle non-determinism with multiple trials.** Run 3–10 independent trials per task. Use isolated environments — Anthropic discovered agents gaining unfair advantages by examining git history from previous trials.

**4. Read the transcripts.** Anthropic's strongest recommendation. Infrastructure bugs frequently masquerade as reasoning failures — a single extraction bug moved one team's benchmark from 50% to 73%.

**5. Integrate evals into CI/CD.** Quality gates with automatic failure on score drops. DeepEval's pytest integration and Braintrust's GitHub Action make this practical today.

**6. Build balanced eval suites.** Test both when behaviors SHOULD and SHOULDN'T occur. One-sided evals create one-sided optimization.

### Three Key Takeaways

**Shift 1 — Output-only → Trajectory-aware evaluation:** Understand WHY agents fail, not just THAT they fail. This means evaluating the entire reasoning and action chain, including tool selection, argument correctness, and step efficiency.

**Shift 2 — OpenTelemetry as the convergence standard:** The GenAI Semantic Conventions prevent vendor lock-in across an increasingly fragmented tool ecosystem. Adopt OTel-compatible instrumentation now.

**Shift 3 — Eval-driven development as a core discipline:** Write evals before writing agent logic. The tooling exists — Inspect AI for capability and safety evaluation, DeepEval for CI/CD-integrated metric coverage, LangSmith or Arize Phoenix for observability, and Azure AI Evaluation for enterprise integration.

> 💡 **Speaker Note:** End with the recommended stack on slide 14, then move to Resources (slide 15). Keep Q&A to 5 minutes. If questions are complex, offer to continue offline.

---

## Appendix: Anticipated Questions

**Q: Which framework should I start with?**
A: If you're in the Azure ecosystem, start with Azure AI Evaluation SDK — it's the fastest path to results. For open-source rigor, Inspect AI. For CI/CD-first developer experience, DeepEval. They're complementary, not competing.

**Q: How many evals do I need before going to production?**
A: Anthropic recommends starting with 20–50 tasks from real failures. You don't need comprehensive coverage on day one — start with the failures that cost the most and expand from there.

**Q: Is LLM-as-judge reliable enough?**
A: At 66% agreement with humans (vs 71% inter-rater), it's close but not equivalent. Use it for scale, calibrate it periodically with human evaluation, and always read transcripts to catch systematic biases.

**Q: What about cost?**
A: The evaluation itself has costs (LLM judge calls), but the cost of shipping a bad agent is much higher. Galileo's Luna-2 runs at roughly $0.02 per million tokens for real-time evaluation. Start with cheap code-based assertions in CI and reserve expensive LLM judges for staging.

**Q: How do we handle the non-determinism problem?**
A: Run 3–10 trials per task, use isolated environments, and report pass@k for development and pass^k for production reliability. Accept that agent evaluation is probabilistic — the goal is statistical confidence, not deterministic certainty.

---

**Deliverables:** Presentation (Evaluating_AI_Agents.pptx) • 01_deepeval_agent_eval.py • 02_inspect_ai_agent_eval.py • 03_azure_ai_eval_agents.py • requirements.txt