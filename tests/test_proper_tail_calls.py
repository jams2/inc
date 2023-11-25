import pytest

from compiler import Var

x = Var("x")
n = Var("n")
ac = Var("ac")
λ = "lambda"


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # deeply nested procedures tests
        [
            (
                "letrec",
                [
                    (
                        "e",
                        (λ, [x], ("if", ("fxzero?", x), True, ["o", ("fxsub1", x)])),
                    ),
                    (
                        "o",
                        (λ, [x], ("if", ("fxzero?", x), False, ["e", ("fxsub1", x)])),
                    ),
                ],
                ["e", 25],
            ),
            "#f\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "countdown",
                        (
                            λ,
                            [n],
                            ("if", ("fxzero?", n), n, ["countdown", ("fxsub1", n)]),
                        ),
                    )
                ],
                ["countdown", 50005000],
            ),
            "0\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "sum",
                        (
                            λ,
                            [n, ac],
                            (
                                "if",
                                ("fxzero?", n),
                                ac,
                                ["sum", ("fxsub1", n), ("fx+", n, ac)],
                            ),
                        ),
                    )
                ],
                ["sum", 10000, 0],
            ),
            "50005000\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "e",
                        (λ, [x], ("if", ("fxzero?", x), True, ["o", ("fxsub1", x)])),
                    ),
                    (
                        "o",
                        (λ, [x], ("if", ("fxzero?", x), False, ["e", ("fxsub1", x)])),
                    ),
                ],
                ["e", 5000000],
            ),
            "#t\n",
        ],
    ],
)
def test_deeply_nested_procedures(program, out, compile_and_run):
    assert compile_and_run(program) == out
