"""
Using the Azure OpenAI Evals API.
"""
import common

client = common.azure_openai_client()
UUID = common.good_enough_uuid()


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
print("> Uploaded file:")
print(file.to_json(indent=2))


## Define our Eval
INPUT = [
    {
        "type": "message",
        "role": "developer",
        "content": {
            "type": "input_text",
            "text": common.GRADER_DEVELOPER_PROMPT,
        },
    },
    {
        "type": "message",
        "role": "user",
        "content": {
            "type": "input_text",
            "text": common.GRADER_USER_PROMPT,
        },
    },
]
SCORE_MODEL_GRADER = {
    "name": "python-checker",
    "type": "score_model",
    "model": common.GRADER_MODEL,
    "input": INPUT,
    "range": [0, 1],
    "pass_threshold": 1,
}
STRING_CHECK_GRADER = {
    "name": "python-string-checker",
    "type": "string_check",
    "operation": "eq",
    "reference": "{{ item.result }}",
    "input": "{{ sample.output_text }}"
}

eval = client.evals.create(
    name=f"{common.EVAL_BASENAME}-{UUID}",
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
    testing_criteria=[SCORE_MODEL_GRADER, STRING_CHECK_GRADER]
)
print("> Created new Eval")
print(eval.to_json(indent=2))

RUN_TEMPLATE = [
    {
        "type": "message",
        "role": "system",
        "content": { "type": "input_text", "text": common.TEST_PROMPT, },
    },
    {
        "type": "message",
        "role": "user",
        "content": { "type": "input_text", "text": "{{ item.code }}", },
    }
]

## Define Test Runs
runs = []
for model in common.TEST_MODELS:
    RUN_DATA_SOURCE = {
        "type": "completions",
        "model": model,
        "source": { "type": "file_id", "id": file.id  },
        "input_messages": {
            "type": "template",
            "template": RUN_TEMPLATE,
        },
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
                "content": { "type": "input_text", "text": common.TEST_PROMPT, },
            },
            {
                "type": "message",
                "role": "user",
                "content": { "type": "input_text", "text": "```python\n{{ item.code }}\n```", },
            }
        ]
    },
    # "sampling_params": { "max_completions_tokens": 1000 }
}