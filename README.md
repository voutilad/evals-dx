## tldr
```
$ python3 -m venv .venv
$ . .venv/bin/activate
(venv)$ pip install -r requirements.txt
```

set an env:

```
$ export AZURE_API_KEY=xxyzzy
$ export AZURE_OPENAI_ENDPOINT="https://..."
$ export PROJECT_ENDPOINT="https://..."
```

then choose your own adventure:

* **aoai** -- `$ python oai-evals.py`
* **foundry** -- `$ python foundry-evals.py`


## the python agent use case
These examples pre-suppose one is building an agent for interpreting Python
code and needing to identify the best base model for the task.

A [dataset](./python.jsonl) is already constructed for the example, but you can
extend the code provided in [quiz.py](./quiz.py) to create a larger or
different dataset.

Once tweaked, just run:

```
$ python3 quiz.py > python.jsonl
```

If you want to check your generate is sound (i.e. produces interpretable
results for this demo), run:

```
$ python3 quiz.py test
```

It will tell if the resulting code in the JSON objects will actually evaluate
to the expected results.
