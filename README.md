# tldr
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