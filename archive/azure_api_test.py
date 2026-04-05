"""test_connection.py — Debug Azure OpenAI connection"""
import os
from dotenv import load_dotenv
load_dotenv()

# 1. Print config (masked)
endpoint = os.environ.get("AZURE_ENDPOINT", "NOT SET")
deployment = os.environ.get("AZURE_DEPLOYMENT_NAME", "NOT SET")
api_key = os.environ.get("AZURE_API_KEY", "NOT SET")
api_version = os.environ.get("AZURE_API_VERSION", "NOT SET")

print(f"Endpoint:    {endpoint}")
print(f"Deployment:  {deployment}")
print(f"API Version: {api_version}")
print(f"API Key:     {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else f"API Key: {api_key}")
print()

# 2. Test raw OpenAI connection (bypasses eval SDK)
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version,
)

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10,
    )
    print(f"✅ Raw OpenAI works! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Raw OpenAI failed: {e}")
    print("\nFix this first before using the evaluation SDK.")
    exit(1)

# 3. Test with eval SDK
print("\nTesting eval SDK...")
from azure.ai.evaluation import AzureOpenAIModelConfiguration, CoherenceEvaluator

model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=endpoint,
    api_key=api_key,
    azure_deployment=deployment,
    api_version=api_version,
)

try:
    evaluator = CoherenceEvaluator(model_config=model_config)
    result = evaluator(query="What is AI?", response="AI is artificial intelligence.")
    print(f"✅ Eval SDK works! Result: {result}")
except Exception as e:
    print(f"❌ Eval SDK failed: {e}")
    print("\nCommon fixes:")
    print("  1. Try api_version='2025-04-01-preview'")
    print("  2. Ensure deployment is a CHAT model (gpt-4o, not embedding)")
    print("  3. Check content filters aren't blocking eval prompts")
    print(f"  4. Current azure-ai-evaluation version:")
    import azure.ai.evaluation
    print(f"     {azure.ai.evaluation.__version__}")