"""
Common stuff.
"""
import os
import uuid

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from azure.ai.evaluation import AzureOpenAIModelConfiguration

# Constants
EVAL_BASENAME = "python-expert"

GRADER_MODEL = "gpt-4.1"

GRADER_DEVELOPER_PROMPT = """
You're an expert Python programmer!

You'll be given python code, a result, and the ground truth.

Your job is to grade if the result provided is the same as the ground truth value.

If it's the same Pythonic value, score it a 1. If it's not or if the result is "Undefined",
score it a 0.

Return your result and reasoning in the following JSON format:

```
  "steps": [
    { 
      "description": <one sentence describing your reasoning>", 
      "result": <string representation the score> 
    }
  ],
  "result": <floating point value of the score>
}
```
"""

GRADER_USER_PROMPT = """
```python
{{ item.code }}
```

Result: {{ sample.output_text }}

Ground Truth: {{ item.result }}
"""

TEST_MODELS = [
    # "gpt-35-turbo",
    "gpt-4.1-nano",
    #"gpt-4.1-mini",
    #"gpt-4.1",
    "gpt-4o-mini",
    #"gpt-4o",
    #"o3-mini",
]

TEST_PROMPT = """
You are an expert Python programmer! When given a snippet of Python code, determine what the
resulting console output would be if executed.

For example, if given the following Python:

```python
def hello()
    return "world"

print(hello)
```

You'd respond with: world

Do not reason about the result. Do not explain the result. Do not format the result. Simply provide the result.

If not result is possible, respond with: undefined
"""

def good_enough_uuid():
    return str(uuid.uuid4()).split("-")[0]

def azure_openai_client():
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT env var missing")

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        api_version="2025-04-01-preview",
        azure_endpoint=endpoint,
        #azure_ad_token_provider=token_provider
        api_key=os.environ.get("AZURE_API_KEY")
    )

def ai_project_client():
    endpoint = os.environ.get("PROJECT_ENDPOINT")
    if not endpoint:
        raise RuntimeError("PROJECT_ENDPOINT env var missing")

    return AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )

def azure_openai_model_config():
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT env var missing")
    key = os.environ.get("AZURE_API_KEY")
    if not key:
        raise RuntimeError("AZURE_API_KEY env var missing")
    
    return AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
        api_key=key,
        azure_deployment=os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4.1"),
        api_version=os.environ.get("AZURE_API_VERSION", "2025-05-01-preview"),
    )