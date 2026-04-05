"""
=============================================================================
03_azure_ai_eval_agents.py — Agent Evaluation with Azure AI Evaluation SDK
=============================================================================
This script demonstrates the three agentic evaluators from Microsoft's
Azure AI Evaluation SDK:
    1. IntentResolutionEvaluator — Did the agent understand the user's goal?
    2. TaskAdherenceEvaluator   — Did the response satisfy the request?
    3. ToolCallAccuracyEvaluator — Were the tool calls correct and efficient?

These evaluators support both simple string inputs and OpenAI-style
agent message schemas.

Requirements:
    pip install azure-ai-evaluation azure-identity python-dotenv

Environment (.env file):
    AZURE_DEPLOYMENT_NAME=gpt-4o
    AZURE_API_KEY=your-azure-openai-key
    AZURE_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_API_VERSION=2024-12-01-preview

    Note: The SDK now requires AzureOpenAIModelConfiguration (not a plain dict).
    Make sure your deployment supports chat completions (gpt-4o, gpt-4.1-mini, etc.).

Reference:
    https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/agent-evaluate-sdk
    https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/evaluating-agentic-ai-systems-a-deep-dive-into-agentic-metrics/4403923
    https://github.com/azure-samples/AgenticEvals
=============================================================================
"""

import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
# IMPORTANT: The latest SDK requires AzureOpenAIModelConfiguration
# instead of a plain dict. This is the recommended approach.

from azure.ai.evaluation import AzureOpenAIModelConfiguration

model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ.get("AZURE_ENDPOINT", ""),
    api_key=os.environ.get("AZURE_API_KEY", ""),
    azure_deployment=os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o"),
    api_version=os.environ.get("AZURE_API_VERSION", "2024-12-01-preview"),
)

# For reasoning models (o3-mini, o1, etc.) — better for complex evals
# Uncomment and configure if you have a reasoning model deployed:
# reasoning_model_config = AzureOpenAIModelConfiguration(
#     azure_endpoint=os.environ.get("AZURE_ENDPOINT", ""),
#     api_key=os.environ.get("AZURE_API_KEY", ""),
#     azure_deployment=os.environ.get("AZURE_REASONING_MODEL", "o3-mini"),
#     api_version=os.environ.get("AZURE_API_VERSION", "2024-12-01-preview"),
# )


# ─────────────────────────────────────────────
# EXAMPLE 1: Intent Resolution Evaluator
# ─────────────────────────────────────────────
# Measures how well the agent identifies and understands
# the user's request. Outputs a Likert score (1-5).

def example_1_intent_resolution():
    """
    Evaluate whether the agent correctly understood
    the user's underlying intent.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Intent Resolution Evaluator")
    print("=" * 70)

    from azure.ai.evaluation import IntentResolutionEvaluator

    # Initialize evaluator with optional binary threshold
    intent_eval = IntentResolutionEvaluator(
        model_config=model_config,
        threshold=3,  # Scores >= 3 → "pass", < 3 → "fail"
    )

    # ── Test Case 1: Clear intent match ──
    result_1 = intent_eval(
        query=[
            {
                "role": "user",
                "content": [{"type": "text", "text": "What are the opening hours of the Eiffel Tower?"}],
            }
        ],
        response=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "The Eiffel Tower is open daily from 9:00 AM to 11:00 PM "
                            "during summer months, and 9:30 AM to 10:30 PM in winter."
                        ),
                    }
                ],
            }
        ],
    )
    print(f"\nTest 1 - Clear Intent:")
    print(f"  Score: {result_1.get('intent_resolution', 'N/A')}")
    print(f"  Result: {result_1.get('intent_resolution_result', 'N/A')}")
    print(f"  Reason: {result_1.get('intent_resolution_reason', 'N/A')}")

    # ── Test Case 2: Misunderstood intent ──
    result_2 = intent_eval(
        query=[
            {
                "role": "user",
                "content": [{"type": "text", "text": "How do I return a damaged laptop?"}],
            }
        ],
        response=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Our laptops come with Intel i7 processors and 16GB RAM. "
                            "They feature a 15.6 inch display with anti-glare coating."
                        ),
                    }
                ],
            }
        ],
    )
    print(f"\nTest 2 - Misunderstood Intent:")
    print(f"  Score: {result_2.get('intent_resolution', 'N/A')}")
    print(f"  Result: {result_2.get('intent_resolution_result', 'N/A')}")

    # ── Test Case 3: Agent asks clarifying questions ──
    result_3 = intent_eval(
        query=[
            {
                "role": "user",
                "content": [{"type": "text", "text": "I need help with my order"}],
            }
        ],
        response=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "I'd be happy to help with your order! Could you please "
                            "provide your order number? Also, are you looking to track "
                            "the shipment, request a return, or something else?"
                        ),
                    }
                ],
            }
        ],
    )
    print(f"\nTest 3 - Clarification (should score well):")
    print(f"  Score: {result_3.get('intent_resolution', 'N/A')}")
    print(f"  Result: {result_3.get('intent_resolution_result', 'N/A')}")


# ─────────────────────────────────────────────
# EXAMPLE 2: Task Adherence Evaluator
# ─────────────────────────────────────────────
# Evaluates whether the agent's final response satisfies
# the original user request. Current SDK behavior is binary
# (1.0 pass / 0.0 fail) based on a flagged decision.

def example_2_task_adherence():
    """
    Evaluate how well the agent's response satisfies
    the user's task requirements.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Task Adherence Evaluator")
    print("=" * 70)

    from azure.ai.evaluation import TaskAdherenceEvaluator

    task_eval = TaskAdherenceEvaluator(
        model_config=model_config,
        # For binary output, 0.5 cleanly separates pass/fail.
        threshold=0.5,
    )

    # ── Test Case 1: Complete task fulfillment ──
    result_1 = task_eval(
        query=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Compare the prices of flights from NYC to London "
                            "for next week and recommend the cheapest option."
                        ),
                    }
                ],
            }
        ],
        response=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_flights_001",
                        "name": "search_flights",
                        "arguments": {
                            "origin": "NYC",
                            "destination": "LON",
                            "date_range": "next week",
                        },
                    }
                ],
            }
            ,
            {
                "role": "tool",
                "tool_call_id": "call_flights_001",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": [
                            {
                                "airline": "British Airways",
                                "price": 620,
                                "duration": "7h",
                                "stops": 0,
                            },
                            {
                                "airline": "Virgin Atlantic",
                                "price": 580,
                                "duration": "7.5h",
                                "stops": 0,
                            },
                            {
                                "airline": "Norse Atlantic",
                                "price": 420,
                                "duration": "10h",
                                "stops": 1,
                            },
                        ],
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "I found 3 flights for next week:\n"
                            "1. British Airways - $620 (direct, 7h)\n"
                            "2. Virgin Atlantic - $580 (direct, 7.5h)\n"
                            "3. Norse Atlantic - $420 (1 stop, 10h)\n\n"
                            "Recommendation: Norse Atlantic at $420 is the cheapest, "
                            "though it has a stop. For direct flights, Virgin Atlantic "
                            "at $580 offers the best value."
                        ),
                    }
                ],
            },
        ],
    )
    print(f"\nTest 1 - Complete Fulfillment:")
    print(f"  Score: {result_1.get('task_adherence', 'N/A')}")
    print(f"  Result: {result_1.get('task_adherence_result', 'N/A')}")
    print(f"  Reason: {result_1.get('task_adherence_reason', 'N/A')}")

    # ── Test Case 2: Partial fulfillment ──
    result_2 = task_eval(
        query=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Compare the prices of flights from NYC to London "
                            "for next week and recommend the cheapest option."
                        ),
                    }
                ],
            }
        ],
        response=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Flights to London are available from around $400-$700.",
                    }
                ],
            }
        ],
    )
    print(f"\nTest 2 - Partial Fulfillment:")
    print(f"  Score: {result_2.get('task_adherence', 'N/A')}")
    print(f"  Result: {result_2.get('task_adherence_result', 'N/A')}")
    print(f"  Reason: {result_2.get('task_adherence_reason', 'N/A')}")


# ─────────────────────────────────────────────
# EXAMPLE 3: Tool Call Accuracy Evaluator
# ─────────────────────────────────────────────
# Measures accuracy and efficiency of tool calls.
# Outputs a float (0-1) representing the passing rate.

def example_3_tool_call_accuracy():
    """
    Evaluate whether the agent made correct and efficient
    tool calls for the given user query.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Tool Call Accuracy Evaluator")
    print("=" * 70)

    from azure.ai.evaluation import ToolCallAccuracyEvaluator

    tool_eval = ToolCallAccuracyEvaluator(
        model_config=model_config,
        threshold=0.8,
    )

    # ── Test Case: Tool calls with definitions ──
    # Provide tool definitions so the evaluator knows what's available
    tool_definitions = [
        {
            "name": "search_flights",
            "description": "Search for available flights",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Departure city or airport code",
                    },
                    "destination": {
                        "type": "string",
                        "description": "Arrival city or airport code",
                    },
                    "date": {
                        "type": "string",
                        "description": "Travel date (YYYY-MM-DD)",
                    },
                },
                "required": ["origin", "destination", "date"],
            },
        },
        {
            "name": "get_hotel_prices",
            "description": "Get hotel prices for a destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City to search hotels in",
                    },
                    "checkin": {
                        "type": "string",
                        "description": "Check-in date (YYYY-MM-DD)",
                    },
                    "checkout": {
                        "type": "string",
                        "description": "Check-out date (YYYY-MM-DD)",
                    },
                },
                "required": ["city", "checkin", "checkout"],
            },
        },
    ]

    # Tool calls the agent actually made
    # IMPORTANT: arguments must be a dict, NOT a JSON string
    tool_calls = [
        {
            "type": "tool_call",
            "tool_call_id": "call_search_flights_001",
            "name": "search_flights",
            "arguments": {
                "origin": "JFK",
                "destination": "LHR",
                "date": "2025-07-15",
            },
        },
        {
            "type": "tool_call",
            "tool_call_id": "call_get_hotels_001",
            "name": "get_hotel_prices",
            "arguments": {
                "city": "London",
                "checkin": "2025-07-15",
                "checkout": "2025-07-20",
            },
        },
    ]

    result = tool_eval(
        query=(
            "I want to fly from New York to London on July 15th "
            "and stay for 5 nights. Find me flights and hotels."
        ),
        tool_calls=tool_calls,
        tool_definitions=tool_definitions,
    )

    print(f"\nTool Call Accuracy:")
    print(f"  Score: {result.get('tool_call_accuracy', 'N/A')}")
    print(f"  Result: {result.get('tool_call_accuracy_result', 'N/A')}")
    print(f"  Reason: {result.get('tool_call_accuracy_reason', 'N/A')}")


# ─────────────────────────────────────────────
# EXAMPLE 4: Agent Messages Format (OpenAI-style)
# ─────────────────────────────────────────────
# For complex agent workflows, provide the full
# conversation thread as OpenAI-style messages.
# This example evaluates the final assistant answer while
# keeping the full trace visible for reference.

def example_4_agent_messages_format():
    """
    Demonstrate OpenAI-style message history and evaluate
    the final assistant answer extracted from that trace.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Agent Messages Format (Trace + Final Answer Eval)")
    print("=" * 70)

    from azure.ai.evaluation import (
        IntentResolutionEvaluator,
        TaskAdherenceEvaluator,
    )

    intent_eval = IntentResolutionEvaluator(model_config=model_config)
    task_eval = TaskAdherenceEvaluator(model_config=model_config)

    # Full conversation trace as OpenAI-style messages
    messages = [
        {
            "role": "system",
            "content": (
                "You are a travel planning assistant. Help users "
                "plan trips by searching flights and hotels."
            ),
        },
        {
            "role": "user",
            "content": (
                "I need to fly from San Francisco to Tokyo next month. "
                "What are my options?"
            ),
        },
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_001",
                    "type": "function",
                    "function": {
                        "name": "search_flights",
                        "arguments": {
                            "origin": "SFO",
                            "destination": "NRT",
                            "date": "2025-08-15",
                        },
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_001",
            "content": json.dumps([
                {
                    "airline": "ANA",
                    "price": 1200,
                    "duration": "11h",
                    "stops": 0,
                },
                {
                    "airline": "United",
                    "price": 980,
                    "duration": "13h",
                    "stops": 1,
                },
                {
                    "airline": "JAL",
                    "price": 1350,
                    "duration": "11.5h",
                    "stops": 0,
                },
            ]),
        },
        {
            "role": "assistant",
            "content": (
                "I found 3 flights from San Francisco to Tokyo:\n\n"
                "1. **ANA** - $1,200 (direct, 11h)\n"
                "2. **United** - $980 (1 stop, 13h)\n"
                "3. **JAL** - $1,350 (direct, 11.5h)\n\n"
                "United is the most affordable at $980, but has a "
                "layover. For a direct flight, ANA at $1,200 is the "
                "best value. Would you like me to book one of these?"
            ),
        },
    ]

    # Build evaluator-friendly conversation inputs from the trace.
    query_messages = [
        {
            "role": "system",
            "content": messages[0]["content"],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": messages[1]["content"]}],
        },
    ]
    response_messages = [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_001",
                    "name": "search_flights",
                    "arguments": {
                        "origin": "SFO",
                        "destination": "NRT",
                        "date": "2025-08-15",
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_001",
            "content": [
                {
                    "type": "tool_result",
                    "tool_result": [
                        {
                            "airline": "ANA",
                            "price": 1200,
                            "duration": "11h",
                            "stops": 0,
                        },
                        {
                            "airline": "United",
                            "price": 980,
                            "duration": "13h",
                            "stops": 1,
                        },
                        {
                            "airline": "JAL",
                            "price": 1350,
                            "duration": "11.5h",
                            "stops": 0,
                        },
                    ],
                }
            ],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": messages[-1]["content"]}],
        },
    ]

    intent_result = intent_eval(query=query_messages, response=response_messages)
    task_result = task_eval(query=query_messages, response=response_messages)

    print(f"\nIntent Resolution: {intent_result.get('intent_resolution', 'N/A')}")
    print(f"Task Adherence: {task_result.get('task_adherence', 'N/A')}")
    print(f"Task Adherence Reason: {task_result.get('task_adherence_reason', 'N/A')}")


# ─────────────────────────────────────────────
# EXAMPLE 5: Batch Evaluation with JSONL Dataset
# ─────────────────────────────────────────────
# Scale evaluations across a dataset using evaluate().

def example_5_batch_evaluation():
    """
    Run batch evaluation across a JSONL dataset.
    Results can be exported to Azure AI Foundry for visualization.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Evaluation with Dataset")
    print("=" * 70)

    from azure.ai.evaluation import (
        evaluate,
        IntentResolutionEvaluator,
        TaskAdherenceEvaluator,
        RelevanceEvaluator,
        CoherenceEvaluator,
    )

    # Create a sample JSONL dataset
    eval_data = [
        {
            "query": "What is your refund policy?",
            "response": (
                "We offer a 30-day money-back guarantee on all products. "
                "Contact support for processing."
            ),
            "query_messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "What is your refund policy?"}],
                }
            ],
            "response_messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "We offer a 30-day money-back guarantee on all products. "
                                "Contact support for processing."
                            ),
                        }
                    ],
                }
            ],
            "context": (
                "Refund policy: 30-day guarantee, full refund, "
                "no questions asked."
            ),
        },
        {
            "query": "How do I track my order?",
            "response": (
                "Log into your account, go to 'My Orders', and click "
                "the tracking number for real-time updates."
            ),
            "query_messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "How do I track my order?"}],
                }
            ],
            "response_messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Log into your account, go to 'My Orders', and click "
                                "the tracking number for real-time updates."
                            ),
                        }
                    ],
                }
            ],
            "context": (
                "Order tracking: Available via My Orders section. "
                "Click tracking number for live updates."
            ),
        },
        {
            "query": "Do you ship internationally?",
            "response": (
                "Yes! We ship to over 50 countries. International "
                "shipping typically takes 7-14 business days. Rates "
                "vary by destination."
            ),
            "query_messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Do you ship internationally?"}],
                }
            ],
            "response_messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Yes! We ship to over 50 countries. International "
                                "shipping typically takes 7-14 business days. Rates "
                                "vary by destination."
                            ),
                        }
                    ],
                }
            ],
            "context": (
                "International shipping: 50+ countries, 7-14 days, "
                "variable rates."
            ),
        },
    ]

    # Write to a temp JSONL file in a cross-platform location.
    eval_file = os.path.join(tempfile.gettempdir(), "eval_data.jsonl")
    with open(eval_file, "w") as f:
        for item in eval_data:
            f.write(json.dumps(item) + "\n")

    # Initialize evaluators
    evaluators = {
        "intent": IntentResolutionEvaluator(model_config=model_config),
        "task_adherence": TaskAdherenceEvaluator(model_config=model_config),
        "relevance": RelevanceEvaluator(model_config=model_config),
        "coherence": CoherenceEvaluator(model_config=model_config),
    }

    # Run batch evaluation
    results = evaluate(
        data=eval_file,
        evaluators=evaluators,
        evaluator_config={
            "intent": {
                "column_mapping": {
                    "query": "${data.query_messages}",
                    "response": "${data.response_messages}",
                },
            },
            "task_adherence": {
                "column_mapping": {
                    "query": "${data.query_messages}",
                    "response": "${data.response_messages}",
                },
            },
            "relevance": {
                "column_mapping": {
                    "response": "${data.response}",
                    "context": "${data.context}",
                    "query": "${data.query}",
                },
            },
        },
    )

    # Print summary
    print(f"\nBatch evaluation completed!")
    print(f"Dataset size: {len(eval_data)} samples")
    print(f"Evaluators: {list(evaluators.keys())}")

    if "metrics" in results:
        print("\nAggregate Metrics:")
        for metric_name, value in results["metrics"].items():
            print(f"  {metric_name}: {value}")

    # Clean up
    os.remove(eval_file)


# ─────────────────────────────────────────────
# EXAMPLE 6: Quality + Safety Combined Evaluation
# ─────────────────────────────────────────────
# Combine agentic quality metrics with safety evaluators.

def example_6_quality_and_safety():
    """
    Combine quality and safety evaluators for a
    comprehensive agent assessment.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Quality + Safety Combined Evaluation")
    print("=" * 70)

    from azure.ai.evaluation import (
        IntentResolutionEvaluator,
        TaskAdherenceEvaluator,
        FluencyEvaluator,
    )

    # Quality evaluators
    quality_evaluators = {
        "intent": IntentResolutionEvaluator(model_config=model_config),
        "task": TaskAdherenceEvaluator(model_config=model_config),
        "fluency": FluencyEvaluator(model_config=model_config),
    }

    # Test with a normal query
    query = "Explain quantum computing in simple terms"
    query_messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": query}],
        }
    ]
    response = (
        "Quantum computing uses quantum bits (qubits) that can be "
        "both 0 and 1 simultaneously, unlike classical bits. This "
        "allows quantum computers to process many possibilities at "
        "once, making them powerful for specific problems like drug "
        "discovery and cryptography."
    )
    response_messages = [
        {
            "role": "assistant",
            "content": [{"type": "text", "text": response}],
        }
    ]

    print("\nRunning quality evaluators...")
    for name, evaluator in quality_evaluators.items():
        if name in ("intent", "task"):
            result = evaluator(query=query_messages, response=response_messages)
        else:
            result = evaluator(response=response)
        score_key = list(result.keys())[0]  # Get the score key
        print(f"  {name}: {result.get(score_key, 'N/A')}")
        if name == "intent":
            print(f"    reason: {result.get('intent_resolution_reason', 'N/A')}")
        if name == "task":
            print(f"    reason: {result.get('task_adherence_reason', 'N/A')}")

    # Note: Safety evaluators (ContentSafetyEvaluator,
    # IndirectAttackEvaluator, CodeVulnerabilityEvaluator)
    # require an Azure AI Foundry project connection.
    # See: https://learn.microsoft.com/en-us/azure/ai-foundry/
    #      concepts/evaluation-evaluators/agent-evaluators
    print("\n  Note: Safety evaluators require Azure AI Foundry project.")
    print("  Supported: Violence, Self-harm, Sexual, HateUnfairness,")
    print("  IndirectAttack, ProtectedMaterials, CodeVulnerability")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Azure AI Evaluation SDK — Agent Evaluation Examples")
    print("=" * 70)

    if not os.environ.get("AZURE_API_KEY"):
        print("\n⚠️  AZURE_API_KEY not set. These examples require")
        print("   Azure OpenAI credentials. Set up your .env file:")
        print("   AZURE_DEPLOYMENT_NAME=gpt-4o")
        print("   AZURE_API_KEY=your-key")
        print("   AZURE_ENDPOINT=https://your-resource.openai.azure.com/")
        print("   AZURE_API_VERSION=2024-12-01-preview")
        print("\nShowing code structure without executing API calls.")
    else:
        example_1_intent_resolution()
        example_2_task_adherence()
        example_3_tool_call_accuracy()
        example_4_agent_messages_format()
        example_5_batch_evaluation()
        example_6_quality_and_safety()

    print("\n\n" + "=" * 70)
    print("For CI/CD with Azure, see: github.com/microsoft/ai-agent-evals")
    print("=" * 70)