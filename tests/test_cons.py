import pytest

cons = "cons"


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [(cons, 1, 2), "(1 . 2)\n"],
        [(cons, 1, ()), "(1)\n"],
        [(cons, (), ()), "(())\n"],
        [(cons, (cons, "a", "b"), ()), "((#\\a . #\\b))\n"],
        [(cons, 1, (cons, 2, (cons, 3, ()))), "(1 2 3)\n"],
        [
            (cons, (cons, 12, (cons, 13, (cons, 14, ()))), (cons, 2, (cons, 3, ()))),
            "((12 13 14) 2 3)\n",
        ],
        [
            (cons, (cons, 12, (cons, 13, (cons, 14, ()))), (cons, (cons, True, False), (cons, 3, ()))),
            "((12 13 14) (#t . #f) 3)\n",
        ],
    ],
)
def test_cons(program, out, compile_and_run):
    assert compile_and_run(program) == out
