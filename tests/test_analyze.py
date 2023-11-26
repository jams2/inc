import pytest

from compiler.analyze import annotate_freevars, convert_closures
from compiler.var import Var

x = Var("x")
y = Var("y")
z = Var("z")
λ = "lambda"


@pytest.mark.parametrize(
    ("p", "q"),
    [
        [(λ, [], x), (λ, [], [x], x)],
        [(λ, [x], x), (λ, [x], [], x)],
        [
            (λ, [x, y], ("fx+", x, y)),
            (λ, [x, y], [], ("fx+", x, y)),
        ],
        [
            (λ, [x], ("fx+", x, y)),
            (λ, [x], [y], ("fx+", x, y)),
        ],
        [
            (λ, [], ("fx+", x, y)),
            (λ, [], [x, y], ("fx+", x, y)),
        ],
        [
            (λ, [y], (λ, [], ("fx+", x, y))),
            (λ, [y], [x], (λ, [], [x, y], ("fx+", x, y))),
        ],
        [
            (λ, [], ("let", [(x, True)], x)),
            (λ, [], [], ("let", [(x, True)], x)),
        ],
        [
            (λ, [x], ("let", [(x, True)], x)),
            (λ, [x], [], ("let", [(x, True)], x)),
        ],
        [
            (λ, [], ("let", [(x, True)], y)),
            (λ, [], [y], ("let", [(x, True)], y)),
        ],
        [
            (λ, [y], ("let", [(x, True)], (λ, [], ("cons", y, z)))),
            (λ, [y], [z], ("let", [(x, True)], (λ, [], [y, z], ("cons", y, z)))),
        ],
        [
            (λ, [y], ("let*", [(x, True)], (λ, [], ("cons", y, z)))),
            (λ, [y], [z], ("let*", [(x, True)], (λ, [], [y, z], ("cons", y, z)))),
        ],
    ],
)
def test_annotate_freevars(p, q):
    assert annotate_freevars(p) == q


@pytest.mark.parametrize(
    ("p", "q"),
    [
        (
            ["let", [(x, 5)], (λ, [y], (λ, [], ("fx+", x, y)))],
            [
                "labels",
                [
                    (
                        "f0",
                        (
                            "code",
                            [],
                            [x, y],
                            ("fx+", x, y),
                        ),
                    ),
                    (
                        "f1",
                        (
                            "code",
                            [y],
                            [x],
                            ("closure", "f0", x, y),
                        ),
                    ),
                ],
                ["let", [(x, 5)], ("closure", "f1", x)],
            ],
        )
    ],
)
def test_convert_closures(p, q):
    analyze = annotate_freevars >= convert_closures
    assert analyze(p) == q
