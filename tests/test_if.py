import pytest


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("if", True, 12, 13), "12\n"],
        [("if", False, 12, 13), "13\n"],
        [("if", 0, 12, 13), "12\n"],
        [("if", (), 43, ()), "43\n"],
        [("if", True, ("if", 12, 13, 4), 17), "13\n"],
        [("if", False, 12, ("if", False, 13, 4)), "4\n"],
        [("if", "X", ("if", 1, 2, 3), ("if", 4, 5, 6)), "2\n"],
        [("if", ("not", ("boolean?", True)), 15, ("boolean?", False)), "#t\n"],
        [
            (
                "if",
                ("if", ("char?", "a"), ("boolean?", "b"), ("fixnum?", "c")),
                119,
                -23,
            ),
            "-23\n",
        ],
        [("if", ("if", ("if", ("not", 1), ("not", 2), ("not", 3)), 4, 5), 6, 7), "6\n"],
        [
            (
                "if",
                ("not", ("if", ("if", ("not", 1), ("not", 2), ("not", 3)), 4, 5)),
                6,
                7,
            ),
            "7\n",
        ],
        [
            (
                "not",
                (
                    "if",
                    ("not", ("if", ("if", ("not", 1), ("not", 2), ("not", 3)), 4, 5)),
                    6,
                    7,
                ),
            ),
            "#f\n",
        ],
        [("if", ("char?", 12), 13, 14), "14\n"],
        [("if", ("char?", "a"), 13, 14), "13\n"],
        [("fxadd1", ("if", ("fxsub1", 1), ("fxsub1", 13), 14)), "13\n"],
    ],
)
def test_if(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [["and"], "#t\n"],
        [["and", True], "#t\n"],
        [["and", False], "#f\n"],
        [["and", True, 1], "1\n"],
        [["and", False, 1], "#f\n"],
        [["and", 1, 1, 3], "3\n"],
        [["and", ["and"], 13], "13\n"],
        [["and", ["and", False], 13], "#f\n"],
    ],
)
def test_and(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [["or"], "#f\n"],
        [["or", 1], "1\n"],
        [["or", 1, False], "1\n"],
        [["or", ["or"]], "#f\n"],
        [["or", ["or", False], 13], "13\n"],
        [["or", ["null?", ()]], "#t\n"],
        [["or", ["null?", True], ["fixnum?", ["char->fixnum", "a"]]], "#t\n"],
    ],
)
def test_or(program, out, compile_and_run):
    assert compile_and_run(program) == out
