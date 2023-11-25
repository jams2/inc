# compiler

It's a Scheme-ish to x86-64 compiler, as described in Abdulaziz Ghuloum's [tutorial](./tutorial.pdf), implemented in Python.

## Why Python?

The tutorial is in Scheme, and I find implementing ideas from a paper or tutorial in a different language beneficial as it forces me to think about the concepts.

## Input language

The input representation is Python:

- Scheme lists can be represented as Python lists or tuples (interchangeably);
- variables are represented as `Var(name: str)`;
- keywords and primitive names are represented as `strs`, e.g. `"letrec"`, `"let"`, `"if"`;
- fixnums are `ints`;
- booleans are `True` and `False`;
- chars are strings of length 1; and
- lambda is the string "lambda".

The compiler CLI `evals` the input program text in an environment with the following bindings, to make writing programs a little easier:

```python
builtins = {
    "λ": "lambda",
    "letrec": "letrec",
    "f": "f",
    "g": "g",
    **{c: Var(c) for c in ("x", "y", "t")},
}
```

Here's an example program:

```python
[
    letrec,
    [
        ("even?", [λ, [x], ("if", ["fx=", x, 0], True, ["odd?", ("fxsub1", x)])]),
        ("odd?", [λ, [x], ("if", ["fx=", x, 0], False, ["even?", ("fxsub1", x)])]),
    ],
    ("even?", 4),
]
```

## Usage examples

Show help text:

```sh
python -m compiler --help
```

Print the assembly listing for `program.py` to stdout:

```sh
python -m compiler -p -f program.py
```

Print the listing for the program read from stdin:

```sh
python -m compiler -p -i <<EOF
[letrec, [("id", [λ, [x], x])], ("id", True)]
EOF
```

Compile and execute `program.py`, print the result to stdout:

```sh
python -m compiler -x -f program.py
```

Read the program from stdin, write the listing to `stst.s`, and compile it for debugging as `stst`:

```sh
python -m compiler -p -i <<EOF > stst.s && make debug
("fxadd1", 41)
EOF
```
