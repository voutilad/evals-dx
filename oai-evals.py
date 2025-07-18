import json
import os
import uuid

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
if not AZURE_OPENAI_ENDPOINT:
    raise RuntimeError("AZURE_OPENAI_ENDPOINT env var missing")

UUID = str(uuid.uuid4()).split("-")[0]

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    api_version="2025-04-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_ad_token_provider=token_provider
)

## Upload our Test Prompts
file = None
for page in client.files.list(purpose="evals").iter_pages():
    for item in page:
        if item.filename == "python.jsonl":
            file = item
            break
if file:
    client.files.delete(file.id)
# upload a new copy
with open("./python.jsonl", mode="rb") as f:
    file = client.files.create(file=f, purpose="evals")
    file = client.files.wait_for_processing(file.id)
print("> Using file:")
print(file.to_json(indent=2))

## Define our Eval
GRADER_MODEL = "o3-mini"
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
INPUT = [
    { "type": "message", "role": "developer", "content": { "type": "input_text", "text": GRADER_DEVELOPER_PROMPT }},
    { "type": "message", "role": "user", "content": { "type": "input_text", "text": GRADER_USER_PROMPT }},
]

eval = client.evals.create(
    name=f"factchecker-{UUID}",
    data_source_config={
        "item_schema": {
            "type": "object",
            "properties": {
                "code": { "type": "string" },
                "result": { "type": "string" },   
            }
        },
        "include_sample_schema": True,
        "type": "custom",
    },
    testing_criteria=[{
        "name": "python-checker",
        "type": "score_model",
        "model": GRADER_MODEL,
        "input": INPUT,
        "range": [0, 1],
        "pass_threshold": 1,
    }]
)
print("> Created new Eval")
print(eval.to_json(indent=2))

## Define Test Runs
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
TEST_MODELS = [
    "gpt-4.1-nano",
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1",
    "o3-mini",
]

runs = []
for model in TEST_MODELS:
    RUN_DATA_SOURCE = {
        "type": "completions",
        "model": model,
        "source": { "type": "file_id", "id": file.id  },
        "input_messages": {
            "type": "template",
            "template": [
                {
                    "type": "message",
                    "role": "system",
                    "content": { "type": "input_text", "text": TEST_PROMPT, },
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": { "type": "input_text", "text": "```python\n{{ item.code }}\n```", },
                }
            ]
        },
        "sampling_params": { "max_completions_tokens": 1000 }
    }
    run = client.evals.runs.create(
        name=f"{model}",
        eval_id=eval.id,
        data_source=RUN_DATA_SOURCE,
    )
    runs.append(run)

print("> Created runs:")
for run in runs:
    print(run.to_json(indent=2))

