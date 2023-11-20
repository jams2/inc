import pytest

from compiler import FXUPPER


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fx+", 1, 2), "3\n"],
        [("fx+", 1, -2), "-1\n"],
        [("fx+", -1, 2), "1\n"],
        [("fx+", -1, -2), "-3\n"],
        [("fx+", 536870911, -1), "536870910\n"],
        [("fx+", 536870910, 1), "536870911\n"],
        [("fx+", -536870912, 1), "-536870911\n"],
        [("fx+", -536870911, -1), "-536870912\n"],
        [("fx+", 536870911, -536870912), "-1\n"],
        [("fx+", 1, ("fx+", 2, 3)), "6\n"],
        [("fx+", 1, ("fx+", 2, -3)), "0\n"],
        [("fx+", 1, ("fx+", -2, 3)), "2\n"],
        [("fx+", 1, ("fx+", -2, -3)), "-4\n"],
        [("fx+", -1, ("fx+", 2, 3)), "4\n"],
        [("fx+", -1, ("fx+", 2, -3)), "-2\n"],
        [("fx+", -1, ("fx+", -2, 3)), "0\n"],
        [("fx+", -1, ("fx+", -2, -3)), "-6\n"],
        [("fx+", ("fx+", 1, 2), 3), "6\n"],
        [("fx+", ("fx+", 1, 2), -3), "0\n"],
        [("fx+", ("fx+", 1, -2), 3), "2\n"],
        [("fx+", ("fx+", 1, -2), -3), "-4\n"],
        [("fx+", ("fx+", -1, 2), 3), "4\n"],
        [("fx+", ("fx+", -1, 2), -3), "-2\n"],
        [("fx+", ("fx+", -1, -2), 3), "0\n"],
        [("fx+", ("fx+", -1, -2), -3), "-6\n"],
        [
            (
                "fx+",
                (
                    "fx+",
                    (
                        "fx+",
                        ("fx+", ("fx+", ("fx+", ("fx+", ("fx+", 1, 2), 3), 4), 5), 6),
                        7,
                    ),
                    8,
                ),
                9,
            ),
            "45\n",
        ],
        [
            (
                "fx+",
                1,
                (
                    "fx+",
                    2,
                    (
                        "fx+",
                        3,
                        ("fx+", 4, ("fx+", 5, ("fx+", 6, ("fx+", 7, ("fx+", 8, 9))))),
                    ),
                ),
            ),
            "45\n",
        ],
    ],
)
def test_fxplus(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fx-", 1, 2), "-1\n"],
        [("fx-", 1, -2), "3\n"],
        [("fx-", -1, 2), "-3\n"],
        [("fx-", -1, -2), "1\n"],
        [("fx-", 536870910, -1), "536870911\n"],
        [("fx-", 536870911, 1), "536870910\n"],
        [("fx-", -536870911, 1), "-536870912\n"],
        [("fx-", -536870912, -1), "-536870911\n"],
        [("fx-", 1, 536870911), "-536870910\n"],
        [("fx-", -1, 536870911), "-536870912\n"],
        [("fx-", 1, -536870910), "536870911\n"],
        [("fx-", -1, -536870912), "536870911\n"],
        [("fx-", 536870911, 536870911), "0\n"],
        # [("fx-", 536870911, -536870912), "-1\n"], # This line seems to be a comment in the original test suite
        [("fx-", -536870911, -536870912), "1\n"],
        [("fx-", 1, ("fx-", 2, 3)), "2\n"],
        [("fx-", 1, ("fx-", 2, -3)), "-4\n"],
        [("fx-", 1, ("fx-", -2, 3)), "6\n"],
        [("fx-", 1, ("fx-", -2, -3)), "0\n"],
        [("fx-", -1, ("fx-", 2, 3)), "0\n"],
        [("fx-", -1, ("fx-", 2, -3)), "-6\n"],
        [("fx-", -1, ("fx-", -2, 3)), "4\n"],
        [("fx-", -1, ("fx-", -2, -3)), "-2\n"],
        [("fx-", 0, ("fx-", -2, -3)), "-1\n"],
        [("fx-", ("fx-", 1, 2), 3), "-4\n"],
        [("fx-", ("fx-", 1, 2), -3), "2\n"],
        [("fx-", ("fx-", 1, -2), 3), "0\n"],
        [("fx-", ("fx-", 1, -2), -3), "6\n"],
        [("fx-", ("fx-", -1, 2), 3), "-6\n"],
        [("fx-", ("fx-", -1, 2), -3), "0\n"],
        [("fx-", ("fx-", -1, -2), 3), "-2\n"],
        [("fx-", ("fx-", -1, -2), -3), "4\n"],
        [
            (
                "fx-",
                (
                    "fx-",
                    (
                        "fx-",
                        ("fx-", ("fx-", ("fx-", ("fx-", ("fx-", 1, 2), 3), 4), 5), 6),
                        7,
                    ),
                    8,
                ),
                9,
            ),
            "-43\n",
        ],
        [
            (
                "fx-",
                1,
                (
                    "fx-",
                    2,
                    (
                        "fx-",
                        3,
                        ("fx-", 4, ("fx-", 5, ("fx-", 6, ("fx-", 7, ("fx-", 8, 9))))),
                    ),
                ),
            ),
            "5\n",
        ],
    ],
)
def test_fxminus(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxlogand", 3, 7), "3\n"],
        [("fxlogand", 3, 5), "1\n"],
        [("fxlogand", 2346, ("fxlognot", 2346)), "0\n"],
        [("fxlogand", ("fxlognot", 2346), 2346), "0\n"],
        [("fxlogand", 2376, 2376), "2376\n"],
    ],
)
def test_fxlogand(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxlogor", 3, 16), "19\n"],
        [("fxlogor", 3, 5), "7\n"],
        [("fxlogor", 3, 7), "7\n"],
        [("fxlognot", ("fxlogor", ("fxlognot", 7), 1)), "6\n"],
        [("fxlognot", ("fxlogor", 1, ("fxlognot", 7))), "6\n"],
    ],
)
def test_fxlogor(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # fx= tests
        [("fx=", 12, 13), "#f\n"],
        [("fx=", 12, 12), "#t\n"],
        [("fx=", 16, ("fx+", 13, 3)), "#t\n"],
        [("fx=", 16, ("fx+", 13, 13)), "#f\n"],
        [("fx=", ("fx+", 13, 3), 16), "#t\n"],
        [("fx=", ("fx+", 13, 13), 16), "#f\n"],
    ],
)
def test_fx_equals(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # fx< tests
        [("fx<", 12, 13), "#t\n"],
        [("fx<", 12, 12), "#f\n"],
        [("fx<", 13, 12), "#f\n"],
        [("fx<", 16, ("fx+", 13, 1)), "#f\n"],
        [("fx<", 16, ("fx+", 13, 3)), "#f\n"],
        [("fx<", 16, ("fx+", 13, 13)), "#t\n"],
        [("fx<", ("fx+", 13, 1), 16), "#t\n"],
        [("fx<", ("fx+", 13, 3), 16), "#f\n"],
        [("fx<", ("fx+", 13, 13), 16), "#f\n"],
        # fx<= tests
        [("fx<=", 12, 13), "#t\n"],
        [("fx<=", 12, 12), "#t\n"],
        [("fx<=", 13, 12), "#f\n"],
        [("fx<=", 16, ("fx+", 13, 1)), "#f\n"],
        [("fx<=", 16, ("fx+", 13, 3)), "#t\n"],
        [("fx<=", 16, ("fx+", 13, 13)), "#t\n"],
        [("fx<=", ("fx+", 13, 1), 16), "#t\n"],
        [("fx<=", ("fx+", 13, 3), 16), "#t\n"],
        [("fx<=", ("fx+", 13, 13), 16), "#f\n"],
    ],
)
def test_fxlt_fxlte(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # fx> tests
        [("fx>", 12, 13), "#f\n"],
        [("fx>", 12, 12), "#f\n"],
        [("fx>", 13, 12), "#t\n"],
        [("fx>", 16, ("fx+", 13, 1)), "#t\n"],
        [("fx>", 16, ("fx+", 13, 3)), "#f\n"],
        [("fx>", 16, ("fx+", 13, 13)), "#f\n"],
        [("fx>", ("fx+", 13, 1), 16), "#f\n"],
        [("fx>", ("fx+", 13, 3), 16), "#f\n"],
        [("fx>", ("fx+", 13, 13), 16), "#t\n"],
        # fx>= tests
        [("fx>=", 12, 13), "#f\n"],
        [("fx>=", 12, 12), "#t\n"],
        [("fx>=", 13, 12), "#t\n"],
        [("fx>=", 16, ("fx+", 13, 1)), "#t\n"],
        [("fx>=", 16, ("fx+", 13, 3)), "#t\n"],
        [("fx>=", 16, ("fx+", 13, 13)), "#f\n"],
        [("fx>=", ("fx+", 13, 1), 16), "#f\n"],
        [("fx>=", ("fx+", 13, 3), 16), "#t\n"],
        [("fx>=", ("fx+", 13, 13), 16), "#t\n"],
    ],
)
def test_fxgt_fxgte(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # char= tests
        [("char=", "a", "a"), "#t\n"],
        [("char=", "a", "b"), "#f\n"],
        [("char=", "b", "a"), "#f\n"],
        [("char=", "c", "c"), "#t\n"],
        [("char=", "A", "a"), "#f\n"],
        [("char=", "a", "A"), "#f\n"],
        [("char=", "z", "z"), "#t\n"],
        [("char=", " ", " "), "#t\n"],
        [("char=", " ", "a"), "#f\n"],
        [("char=", "0", "0"), "#t\n"],
        [("char=", "0", "1"), "#f\n"],
        [("char=", "1", "0"), "#f\n"],
        [("char=", "1", "1"), "#t\n"],
        # Add more tests as needed
    ],
)
def test_charequal(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        # char< tests
        [("char<", "a", "b"), "#t\n"],
        [("char<", "b", "a"), "#f\n"],
        [("char<", "a", "a"), "#f\n"],
        [("char<", "z", "a"), "#f\n"],
        [("char<", " ", "#"), "#t\n"],
        [("char<", "A", "a"), "#t\n"],
        # char<= tests
        [("char<=", "a", "b"), "#t\n"],
        [("char<=", "b", "a"), "#f\n"],
        [("char<=", "a", "a"), "#t\n"],
        [("char<=", "z", "a"), "#f\n"],
        [("char<=", " ", "#"), "#t\n"],
        [("char<=", "A", "a"), "#t\n"],
        # char> tests
        [("char>", "a", "b"), "#f\n"],
        [("char>", "b", "a"), "#t\n"],
        [("char>", "a", "a"), "#f\n"],
        [("char>", "z", "a"), "#t\n"],
        [("char>", " ", "#"), "#f\n"],
        [("char>", "a", "A"), "#t\n"],
        # char>= tests
        [("char>=", "a", "b"), "#f\n"],
        [("char>=", "b", "a"), "#t\n"],
        [("char>=", "a", "a"), "#t\n"],
        [("char>=", "z", "a"), "#t\n"],
        [("char>=", " ", "#"), "#f\n"],
        [("char>=", "a", "A"), "#t\n"],
    ],
)
def test_char_comparisons(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        (["fx*", 1, 1], "1\n"),
        (["fx*", -1, 1], "-1\n"),
        (["fx*", -1, -1], "1\n"),
        (["fx*", (FXUPPER - 1) // 2, 2], f"{FXUPPER - 1}\n"),
    ],
)
def test_fxmul(program, out, compile_and_run):
    assert compile_and_run(program) == out
