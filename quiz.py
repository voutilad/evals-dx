import inspect

# Some random Python functions for building a dataset.
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

# Quiz questions! Tuples of (function to call, [functions to include in code gen], args to the function)
QUIZ = [
    ([f], f, [[0]]),
    ([g], g, [-1, 3]),
    ([h, g], g, ["hello", "world"]),
    ([z, f], f, [[1, 2]]),
    ([y], y, [[1, 2]]),
    ([y], y, [20]),
    ([g, f, y], y, ["repeat"])
]


def generate_code():
    """
    Generate Python code snippets, evaluate the answer, and construct the quiz data.
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
