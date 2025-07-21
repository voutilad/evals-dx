"""
Using the Azure AI Foundry Evaluations API.
"""
import common
import json

from azure.ai.evaluation  import (
    AzureOpenAIScoreModelGrader, AzureOpenAIStringCheckGrader, evaluate
)

UUID = common.good_enough_uuid()

aoai_client = common.azure_openai_client()
project_client = common.ai_project_client()

## Generate responses from our test models.
# Build chat completions.
results = dict.fromkeys(common.TEST_MODELS)
with open("./python.jsonl", "r") as f:
    for line in f.readlines():
        obj = json.loads(line)
        # save the data form for each model
        for model in common.TEST_MODELS:
            if not results[model]:
                results[model] = []
            results[model].append({
                "code": obj["item"]["code"], 
                "result": obj["item"]["result"],
                "response": None,
            })

# Run them through models, collecting results.
for model in common.TEST_MODELS:
    print(f"> generating {len(results[model])} responses for {model}")
    for obj in results[model]:
        chat = [
            { "role": "system", "content": common.TEST_PROMPT },
            { "role": "user", "content": obj["code"] },
        ]
        completions = aoai_client.chat.completions.create(
            model=model,
            messages=chat,
        )
        obj["response"] = completions.choices[0].message.content.strip()
        print(".", end="", flush=True)
    print("\n")

# Write them out to files in chat completions format.
for model in common.TEST_MODELS:
    with open(f"./python-{model}-{UUID}.jsonl", "w") as f:
        for result in results[model]:
            f.write(json.dumps(result))
            f.write("\n")


## Create evaluations for our models
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
            "text": "{{ item.code }}",
        },
    },
    { 
        "type": "message",
        "role": "assistant",
        "content": {
            "type": "input_text", 
            "text": "{{ item.response }}",
        },
    },
]

python = AzureOpenAIScoreModelGrader(
    model_config=common.azure_openai_model_config(),
    model="gpt-4.1",
    name="PythonScoreGrader",
    pass_threshold=1.0,
    range=[0.0, 1.0],
    input=INPUT,
)
string = AzureOpenAIStringCheckGrader(
    model_config=common.azure_openai_model_config(),    # XXX why is this needed?!
    name="PythonStringGrader",
    operation="eq",
    reference="{{ item.result }}",
    input="{{ item.response }}",
)

evaluator_config = {
    "python": {
        "column_mapping": {
            "code": "$data.code",
            "result": "$data.result",
            "response": "$data.response",
        }
    },
    "string": {
        "column_mapping": {
            "code": "$data.code",
            "result": "$data.result",
            "response": "$data.response",
        }
    },
}
for model in common.TEST_MODELS:
    print(f"> evaluating {model}")
    evaluate(
        data=f"./python-{model}-{UUID}.jsonl",
        evaluation_name=f"foundry-eval-python-{model}",
        evaluators={
            "python": python,
            "string": string,
        },
    )