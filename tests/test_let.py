import pytest

from compiler import Var

x = Var("x")
y = Var("y")
t = Var("t")


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("let", [(x, 5)], x), "5\n"],
        [("let", [(x, ("fx+", 1, 2))], x), "3\n"],
        [
            (
                "let",
                [(x, ("fx+", 1, 2))],
                ("let", [(y, ("fx+", 3, 4))], ("fx+", x, y)),
            ),
            "10\n",
        ],
        [
            (
                "let",
                [(x, ("fx+", 1, 2))],
                ("let", [(y, ("fx+", 3, 4))], ("fx-", y, x)),
            ),
            "4\n",
        ],
        [
            (
                "let",
                [(x, ("fx+", 1, 2)), (y, ("fx+", 3, 4))],
                ("fx-", y, x),
            ),
            "4\n",
        ],
        [
            (
                "let",
                [
                    (
                        x,
                        (
                            "let",
                            [(y, ("fx+", 1, 2))],
                            ("fx*", y, y),
                        ),
                    )
                ],
                ("fx+", x, x),
            ),
            "18\n",
        ],
        [
            (
                "let",
                [(x, ("fx+", 1, 2))],
                ("let", [(x, ("fx+", 3, 4))], x),
            ),
            "7\n",
        ],
        [
            (
                "let",
                [(x, ("fx+", 1, 2))],
                ("let", [(x, ("fx+", x, 4))], x),
            ),
            "7\n",
        ],
        [
            (
                "let",
                [
                    (
                        t,
                        (
                            "let",
                            [
                                (
                                    t,
                                    (
                                        "let",
                                        [
                                            (
                                                t,
                                                (
                                                    "let",
                                                    [(t, ("fx+", 1, 2))],
                                                    t,
                                                ),
                                            )
                                        ],
                                        t,
                                    ),
                                )
                            ],
                            t,
                        ),
                    )
                ],
                t,
            ),
            "3\n",
        ],
        [
            (
                "let",
                [(x, 12)],
                (
                    "let",
                    [(x, ("fx+", x, x))],
                    (
                        "let",
                        [(x, ("fx+", x, x))],
                        (
                            "let",
                            [(x, ("fx+", x, x))],
                            ("fx+", x, x),
                        ),
                    ),
                ),
            ),
            "192\n",
        ],
    ],
)
def test_let(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # let* tests
        [("let*", [(x, 5)], x), "5\n"],
        [("let*", [(x, ("fx+", 1, 2))], x), "3\n"],
        [
            (
                "let*",
                [(x, ("fx+", 1, 2)), (y, ("fx+", 3, 4))],
                ("fx+", x, y),
            ),
            "10\n",
        ],
        [
            (
                "let*",
                [(x, ("fx+", 1, 2)), (y, ("fx+", 3, 4))],
                ("fx-", y, x),
            ),
            "4\n",
        ],
        [
            (
                "let*",
                [
                    (
                        x,
                        (
                            "let*",
                            [(y, ("fx+", 1, 2))],
                            ("fx*", y, y),
                        ),
                    )
                ],
                ("fx+", x, x),
            ),
            "18\n",
        ],
        [
            ("let*", [(x, ("fx+", 1, 2)), (x, ("fx+", 3, 4))], x),
            "7\n",
        ],
        [
            (
                "let*",
                [(x, ("fx+", 1, 2)), (x, ("fx+", x, 4))],
                x,
            ),
            "7\n",
        ],
        [
            [
                "let*",
                [
                    (
                        t,
                        [
                            "let*",
                            [
                                (
                                    t,
                                    [
                                        "let*",
                                        [(t, ["let*", [(t, ("fx+", 1, 2))], t])],
                                        t,
                                    ],
                                )
                            ],
                            t,
                        ],
                    )
                ],
                t,
            ],
            "3\n",
        ],
        [
            (
                "let*",
                [
                    (x, 12),
                    (x, ("fx+", x, x)),
                    (x, ("fx+", x, x)),
                    (x, ("fx+", x, x)),
                ],
                ("fx+", x, x),
            ),
            "192\n",
        ],
        # let vs let* tests
        [
            (
                "let",
                [(x, 1)],
                (
                    "let",
                    [
                        (x, ("fx+", x, 1)),
                        (y, ("fx+", x, 1)),
                    ],
                    y,
                ),
            ),
            "2\n",
        ],
        [
            (
                "let*",
                [(x, 1)],
                (
                    "let*",
                    [
                        (x, ("fx+", x, 1)),
                        (y, ("fx+", x, 1)),
                    ],
                    y,
                ),
            ),
            "3\n",
        ],
    ],
)
def test_let_and_let_star(program, out, compile_and_run):
    assert compile_and_run(program) == out
