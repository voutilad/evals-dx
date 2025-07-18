"""
Generate some Python quiz code for testing an LLM on its Python knowledge and
reasoning ability.

To generate a chat completion compatible dataset (printing to the console):

```bash
python3 quiz.py
```

If you make code changes, you can run a validation to see if the generated
output actually works if evaluated as Python code:

```bash
python3 quiz.py test
```
"""
import inspect

### Some random Python functions for building a dataset.
def f(x):
    x + [1, 2]

def g(x, y):
    return x + y

def h(*args):
    return [str(x) for x in args]

def y(x):
    return x + x

def z(x):
    return f(x) or 10

def a(b: str, c: str, d="dishwasher"):
    return " ".join([b, c, d])

def loaded_dice(n=6):
    sides = [x + 1 for x in list(range(n))]
    return sides[-1]

def tricky(x, y):
    try:
        return x[y]
    except Exception as e:
        return y


### Quiz questions!
# Tuples that look like:
#  (function to call, [functions to include in code gen], args to the function)
QUIZ = [
    ([f], f, [[0]]),
    ([g], g, [-1, 3]),
    ([h, g], g, ["hello", "world"]),
    ([z, f], f, [[1, 2]]),
    ([y], y, [[1, 2]]),
    ([y], y, [20]),
    ([g, f, y], y, ["repeat"]),
    ([a], a, ["purple", "monkey"]),
    ([f, loaded_dice, g], loaded_dice, [3]),
    ([tricky], tricky, [{"name": "Dave"}, "age"])
]


def generate_code():
    """
    Generate Python code snippets, evaluate the answer, and construct the quiz.
    """
    code = []
    for fns, callme, args in QUIZ:
        result = callme(*args)
        code.append({
            "item": {
                "code": f"{"\n".join([inspect.getsource(x) for x in fns])}\nprint({callme.__name__}({", ".join([str(repr(x)) for x in args])}))",
                "result": str(result)
            }
        })
    return code


def test(code = []):
    """
    Validate our quiz data constructs valid results.
    """
    import sys
    from io import StringIO

    # monkeypatch stdout
    old = sys.stdout
    try:
        for idx, c in enumerate(code):
            sys.stdout = StringIO()
            exec(c["item"]["code"])
            result = sys.stdout.getvalue().strip()
            if result == c["item"]["result"]:
                print(f"{idx}: pass", file=old)
            else:
                print(f"{idx}: fail [got {result}, wanted {c["item"]["result"]}]", file=old)
    except Exception as e:
        print(e, file=sys.stderr)
    sys.stdout = old


if __name__ == "__main__":
    import json
    import sys

    code = generate_code()
    if sys.argv[-1] == "test":
        test(code)
    else:
        for c in code:
            print(json.dumps(c))
