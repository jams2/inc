import pytest

from compiler import Var

x = Var("x")
y = Var("y")
acc = Var("acc")
n = Var("n")


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # procedures tests
        [("letrec", [], 12), "12\n"],
        [("letrec", [], ("let", [(x, 5)], ("fx+", x, x))), "10\n"],
        [("letrec", [("f", ("λ", [], 5))], 7), "7\n"],
        [("letrec", [("f", ("λ", [], 5))], ("let", [(x, 12)], x)), "12\n"],
        [("letrec", [("f", ("λ", [], 5))], ["f"]), "5\n"],
        [("letrec", [("f", ("λ", [], 5))], ("let", [(x, ["f"])], x)), "5\n"],
        [("letrec", [("f", ("λ", [], 5))], ("fx+", ["f"], 6)), "11\n"],
        [("letrec", [("f", ("λ", [], 5))], ("fx+", 6, ["f"])), "11\n"],
        [("letrec", [("f", ("λ", [], 5))], ("fx-", 20, ["f"])), "15\n"],
        [("letrec", [("f", ("λ", [], 5))], ("fx+", ["f"], ["f"])), "10\n"],
        [
            (
                "letrec",
                [("f", ("λ", [], ("fx+", 5, 7))), ("g", ("λ", [], 13))],
                ("fx+", ["f"], ["g"]),
            ),
            "25\n",
        ],
        [("letrec", [("f", ("λ", [x], ("fx+", x, 12)))], ["f", 13]), "25\n"],
        [("letrec", [("f", ("λ", [x], ("fx+", x, 12)))], ["f", ["f", 10]]), "34\n"],
        [
            ("letrec", [("f", ("λ", [x], ("fx+", x, 12)))], ["f", ["f", ["f", 0]]]),
            "36\n",
        ],
        [
            (
                "letrec",
                [
                    ("f", ("λ", [x, y], ("fx+", x, y))),
                    ("g", ("λ", [x], ("fx+", x, 12))),
                ],
                ["f", 16, ["f", ["g", 0], ("fx+", 1, ["g", 0])]],
            ),
            "41\n",
        ],
        [
            (
                "letrec",
                [("f", ("λ", [x], ["g", x, x])), ("g", ("λ", [x, y], ("fx+", x, y)))],
                ["f", 12],
            ),
            "24\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "f",
                        (
                            "λ",
                            [x],
                            ("if", ("fxzero?", x), 1, ("fx*", x, ["f", ("fxsub1", x)])),
                        ),
                    )
                ],
                ["f", 5],
            ),
            "120\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "f",
                        (
                            "λ",
                            [x, acc],
                            (
                                "if",
                                ("fxzero?", x),
                                acc,
                                ["f", ("fxsub1", x), ("fx*", acc, x)],
                            ),
                        ),
                    )
                ],
                ["f", 5, 1],
            ),
            "120\n",
        ],
        [
            (
                "letrec",
                [
                    (
                        "f",
                        (
                            "λ",
                            [x],
                            ("if", ("fxzero?", x), 0, ("fx+", 1, ["f", ("fxsub1", x)])),
                        ),
                    )
                ],
                ["f", 200],
            ),
            "200\n",
        ],
        # more stack test
        [
            (
                "letrec",
                [
                    (
                        "f",
                        (
                            "λ",
                            [n],
                            ("if", ("fxzero?", n), 0, ("fx+", 1, ["f", ("fxsub1", n)])),
                        ),
                    )
                ],
                ["f", 500],
            ),
            "500\n",
        ],
        [
            [
                "letrec",
                [
                    (
                        "even",
                        [
                            "lambda",
                            [x],
                            ("if", ["fx=", x, 0], True, ["odd", ("fxsub1", x)]),
                        ],
                    ),
                    (
                        "odd",
                        [
                            "lambda",
                            [x],
                            ("if", ["fx=", x, 0], False, ["even", ("fxsub1", x)]),
                        ],
                    ),
                ],
                ("even", 1001),
            ],
            "#f\n"
        ],
    ],
)
def test_procedures_and_more_stack(program, out, compile_and_run):
    assert compile_and_run(program) == out
