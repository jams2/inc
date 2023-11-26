import pytest

from compiler import Var

cons = "cons"
car = "car"
cdr = "cdr"
x = Var("x")
y = Var("y")


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
            (
                cons,
                (cons, 12, (cons, 13, (cons, 14, ()))),
                (cons, (cons, True, False), (cons, 3, ())),
            ),
            "((12 13 14) (#t . #f) 3)\n",
        ],
        [(car, [cons, 1, 2]), "1\n"],
        [(cdr, [cons, 1, 2]), "2\n"],
    ],
)
def test_cons(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("pair?", (cons, 1, 2)), "#t\n"],
        [("pair?", 1), "#f\n"],
        [("pair?", True), "#f\n"],
        [("pair?", False), "#f\n"],
        [("pair?", ()), "#f\n"],
        [("let*", [(x, (cons, 1, ())), (y, ("pair?", x))], y), "#t\n"],
    ],
)
def test_pairp(program, out, compile_and_run):
    assert compile_and_run(program) == out
