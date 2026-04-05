"""
=============================================================================
01_deepeval_agent_eval.py — AI Agent Evaluation with DeepEval
=============================================================================
This script demonstrates how to evaluate AI agents using DeepEval's
agent-specific metrics: ToolCorrectness, PlanQuality, PlanAdherence,
TaskCompletion, ArgumentCorrectness, and StepEfficiency.

Requirements:
    pip install deepeval openai

Environment:
    export OPENAI_API_KEY="your-key-here"
    # Or use any LLM: Azure OpenAI, Anthropic, Ollama, etc.

Usage:
    python 01_deepeval_agent_eval.py
    # Or with pytest: deepeval test run 01_deepeval_agent_eval.py

Reference:
    https://github.com/confident-ai/deepeval
    https://deepeval.com/guides/guides-ai-agent-evaluation-metrics
=============================================================================
"""

import json
from typing import List, Dict

# ─────────────────────────────────────────────
# SECTION 1: End-to-End Agent Evaluation (Black-Box)
# ─────────────────────────────────────────────
# Evaluate agent outputs without tracing internals.
# Useful for comparing agent versions side-by-side.

from deepeval import evaluate
from deepeval.metrics import (
    GEval,
    AnswerRelevancyMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall
from deepeval.dataset import EvaluationDataset, Golden


def example_1_end_to_end_evaluation():
    """
    Black-box evaluation: test final agent output quality
    without needing to instrument agent internals.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: End-to-End Agent Evaluation (Black-Box)")
    print("=" * 70)

    # Define custom correctness metric using G-Eval (LLM-as-judge)
    task_correctness = GEval(
        name="Task Correctness",
        criteria=(
            "Determine if the 'actual output' correctly addresses the user's "
            "request based on the 'expected output'. Consider completeness, "
            "accuracy, and relevance."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
    )

    # Define answer relevancy metric
    relevancy = AnswerRelevancyMetric(threshold=0.7)

    # Create test cases simulating agent interactions
    test_cases = [
        LLMTestCase(
            input="What is the refund policy for orders over $100?",
            actual_output=(
                "For orders over $100, we offer a 30-day full refund policy. "
                "Simply contact support with your order number."
            ),
            expected_output="30-day full refund for orders over $100",
            retrieval_context=[
                "All orders over $100 are eligible for a 30-day full refund."
            ],
        ),
        LLMTestCase(
            input="How do I track my shipment?",
            actual_output=(
                "You can track your shipment by logging into your account "
                "and navigating to 'Order History'. Click on the tracking "
                "number for real-time updates."
            ),
            expected_output=(
                "Log into account, go to Order History, click tracking number"
            ),
        ),
        LLMTestCase(
            input="Can I change my delivery address after placing an order?",
            actual_output=(
                "Yes, you can change your delivery address within 2 hours "
                "of placing the order. Go to Order Details and click "
                "'Edit Address'."
            ),
            expected_output=(
                "Address changes allowed within 2 hours via Order Details"
            ),
        ),
    ]

    # Run batch evaluation
    results = evaluate(
        test_cases=test_cases,
        metrics=[task_correctness, relevancy],
    )

    # Print summary
    print(f"\nResults: {len(test_cases)} test cases evaluated")
    print(f"Metrics: Task Correctness, Answer Relevancy")


# ─────────────────────────────────────────────
# SECTION 2: Tool Correctness Evaluation
# ─────────────────────────────────────────────
# Evaluate whether the agent selects the right tools.

def example_2_tool_correctness():
    """
    Evaluate whether the agent calls the correct tools
    for a given user query.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Tool Correctness Evaluation")
    print("=" * 70)

    tool_correctness = ToolCorrectnessMetric(threshold=0.7)

    # Simulate an agent that should call search_flights + book_hotel
    test_case = LLMTestCase(
        input="Book me a flight from NYC to London and a hotel for June 2025",
        actual_output="I found 3 flights and 5 hotels for your trip.",
        # Tools the agent actually called
        tools_called=[
            ToolCall(name="search_flights", input_params={
                "origin": "NYC", "destination": "London", "date": "2025-06-01"
            }),
            ToolCall(name="search_hotels", input_params={
                "city": "London", "checkin": "2025-06-01", "checkout": "2025-06-07"
            }),
        ],
        # Tools expected to be called (ground truth)
        expected_tools=[
            ToolCall(name="search_flights"),
            ToolCall(name="search_hotels"),
        ],
    )

    tool_correctness.measure(test_case)
    print(f"Tool Correctness Score: {tool_correctness.score:.2f}")
    print(f"Reason: {tool_correctness.reason}")


# ─────────────────────────────────────────────
# SECTION 3: Component-Level Evaluation with Tracing
# ─────────────────────────────────────────────
# Use @observe decorator to trace agent internals and
# evaluate at the component level.

from deepeval.tracing import observe, update_current_span
from deepeval.metrics import PlanQualityMetric, PlanAdherenceMetric


def example_3_component_level_tracing():
    """
    White-box evaluation using @observe decorator.
    Traces agent internals for component-level metrics.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Component-Level Evaluation with Tracing")
    print("=" * 70)

    # Initialize agent-specific metrics
    plan_quality = PlanQualityMetric(threshold=0.7)
    plan_adherence = PlanAdherenceMetric(threshold=0.7)
    tool_correctness = ToolCorrectnessMetric(threshold=0.7)

    # ── Simulated Agent with Tracing ──

    @observe(type="tool")
    def search_flights(origin: str, destination: str, date: str) -> list:
        """Search for available flights."""
        return [
            {"id": "FL123", "price": 450, "airline": "BA"},
            {"id": "FL456", "price": 380, "airline": "VS"},
        ]

    @observe(type="tool")
    def book_flight(flight_id: str) -> dict:
        """Book a specific flight."""
        return {"confirmation": "BK-789", "status": "confirmed"}

    @observe(type="llm", metrics=[plan_quality, tool_correctness])
    def agent_reasoning(query: str):
        """Agent's LLM reasoning component."""
        # Simulate reasoning: plan + tool calls
        flights = search_flights("NYC", "London", "2025-06-01")
        best = min(flights, key=lambda f: f["price"])
        booking = book_flight(best["id"])

        # Update span with test case data for metric evaluation
        update_current_span(
            test_case=LLMTestCase(
                input=query,
                actual_output=(
                    f"Booked flight {best['id']} at ${best['price']}. "
                    f"Confirmation: {booking['confirmation']}"
                ),
                tools_called=[
                    ToolCall(name="search_flights", input_params={
                        "origin": "NYC", "destination": "London"
                    }),
                    ToolCall(name="book_flight", input_params={
                        "flight_id": best["id"]
                    }),
                ],
                expected_tools=[
                    ToolCall(name="search_flights"),
                    ToolCall(name="book_flight"),
                ],
            )
        )
        return booking

    @observe(type="agent", metrics=[plan_adherence])
    def travel_agent(query: str):
        """Top-level agent orchestrator."""
        result = agent_reasoning(query)
        update_current_span(
            test_case=LLMTestCase(
                input=query,
                actual_output=f"Trip booked: {result['confirmation']}",
            )
        )
        return result

    # ── Run with Dataset ──
    dataset = EvaluationDataset(goldens=[
        Golden(input="Find the cheapest flight from NYC to London in June 2025"),
        Golden(input="Book a round-trip flight from SF to Tokyo next month"),
    ])

    for golden in dataset.evals_iterator():
        travel_agent(golden.input)

    print("Component-level evaluation complete!")
    print("Check Confident AI dashboard or local output for detailed results.")


# ─────────────────────────────────────────────
# SECTION 4: Custom Metric with DAG (Deterministic)
# ─────────────────────────────────────────────
# DeepEval v3.0 DAG metric: deterministic LLM-as-judge
# using decision trees for consistent scoring.

def example_4_custom_geval_metric():
    """
    Create a custom evaluation metric using G-Eval
    for domain-specific agent quality assessment.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom G-Eval Metric for Agent Quality")
    print("=" * 70)

    # Custom metric: evaluate if agent properly handles edge cases
    edge_case_handling = GEval(
        name="Edge Case Handling",
        criteria=(
            "Evaluate whether the agent properly handles edge cases in the "
            "user's request. Consider: (1) Does the agent acknowledge when "
            "information is insufficient? (2) Does it ask clarifying questions "
            "when needed? (3) Does it avoid hallucinating unsupported details?"
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.6,
    )

    # Test with an ambiguous query
    test_case = LLMTestCase(
        input="Book me a flight",  # Deliberately vague
        actual_output=(
            "I'd be happy to help you book a flight! Could you please "
            "provide the following details?\n"
            "1. Departure city\n"
            "2. Destination city\n"
            "3. Travel date(s)\n"
            "4. Number of passengers\n"
            "5. Any preferences (class, airline)?"
        ),
    )

    edge_case_handling.measure(test_case)
    print(f"Edge Case Handling Score: {edge_case_handling.score:.2f}")
    print(f"Reason: {edge_case_handling.reason}")


# ─────────────────────────────────────────────
# SECTION 5: Pytest Integration for CI/CD
# ─────────────────────────────────────────────
# Run with: deepeval test run 01_deepeval_agent_eval.py

import pytest
from deepeval import assert_test


def test_agent_tool_selection():
    """
    CI/CD-ready test: fails the pipeline if tool correctness
    drops below threshold.

    Run: deepeval test run 01_deepeval_agent_eval.py -n 4
    """
    tool_metric = ToolCorrectnessMetric(threshold=0.8)
    test_case = LLMTestCase(
        input="Search for Italian restaurants near me",
        actual_output="Found 5 Italian restaurants within 2 miles.",
        tools_called=[
            ToolCall(name="search_restaurants", input_params={
                "cuisine": "Italian", "radius_miles": 2
            }),
        ],
        expected_tools=[ToolCall(name="search_restaurants")],
    )
    assert_test(test_case, [tool_metric])


def test_agent_response_quality():
    """
    CI/CD-ready test: fails if response quality is below threshold.
    """
    quality_metric = GEval(
        name="Response Quality",
        criteria="Is the response helpful, accurate, and well-structured?",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.7,
    )
    test_case = LLMTestCase(
        input="What is the weather like in London today?",
        actual_output=(
            "Currently in London it's 15°C with partly cloudy skies. "
            "Expected high of 18°C. Light rain possible this afternoon."
        ),
    )
    assert_test(test_case, [quality_metric])


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("DeepEval AI Agent Evaluation Examples")
    print("=" * 70)

    # Run examples (comment out as needed)
    example_1_end_to_end_evaluation()
    example_2_tool_correctness()
    example_3_component_level_tracing()
    example_4_custom_geval_metric()

    print("\n\n" + "=" * 70)
    print("For CI/CD, run: deepeval test run 01_deepeval_agent_eval.py")
    print("=" * 70)
