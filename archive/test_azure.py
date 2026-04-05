import os

import pytest
from dotenv import load_dotenv
from azure.ai.evaluation import AzureOpenAIModelConfiguration, CoherenceEvaluator


load_dotenv()


def test_azure_coherence_evaluator_smoke():
    """Run a minimal Azure AI Evaluation smoke test with coherence scoring."""
    required_env = ["AZURE_ENDPOINT", "AZURE_API_KEY", "AZURE_DEPLOYMENT_NAME"]
    missing = [name for name in required_env if not os.environ.get(name)]
    if missing:
        pytest.skip(
            "Skipping Azure evaluation smoke test; missing env vars: "
            + ", ".join(missing)
        )

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_ENDPOINT"],
        api_key=os.environ["AZURE_API_KEY"],
        azure_deployment=os.environ["AZURE_DEPLOYMENT_NAME"],
        api_version=os.environ.get("AZURE_API_VERSION", "2024-12-01-preview"),
    )

    evaluator = CoherenceEvaluator(model_config=model_config)
    result = evaluator(
        query="What is AI?",
        response="AI stands for artificial intelligence.",
    )

    # Keep assertions stable across model/evaluator updates.
    assert isinstance(result, dict)
    assert "coherence" in result
    assert isinstance(result["coherence"], (int, float))