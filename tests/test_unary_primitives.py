import pytest

from compiler import FXLOWER, FXUPPER


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxadd1", 0), "1\n"],
        [("fxadd1", -1), "0\n"],
        [("fxadd1", 1), "2\n"],
        [("fxadd1", -100), "-99\n"],
        [("fxadd1", 1000), "1001\n"],
        [("fxadd1", 536870910), "536870911\n"],
        [("fxadd1", -536870912), "-536870911\n"],
        [("fxadd1", ("fxadd1", 0)), "2\n"],
        [
            ("fxadd1", ("fxadd1", ("fxadd1", ("fxadd1", ("fxadd1", ("fxadd1", 12)))))),
            "18\n",
        ],
    ],
)
def test_fxadd1(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxsub1", 0), "-1\n"],
        [("fxsub1", -1), "-2\n"],
        [("fxsub1", 1), "0\n"],
        [("fxsub1", -100), "-101\n"],
        [("fxsub1", 1000), "999\n"],
        [("fxsub1", 536870911), "536870910\n"],
        [("fxsub1", -536870911), "-536870912\n"],
        [("fxsub1", ("fxsub1", 0)), "-2\n"],
        [
            ("fxsub1", ("fxsub1", ("fxsub1", ("fxsub1", ("fxsub1", ("fxsub1", 12)))))),
            "6\n",
        ],
        [("fxsub1", ("fxadd1", 0)), "0\n"],
    ],
)
def test_fxsub1(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fixnum->char", 65), "#\\A\n"],
        [("fixnum->char", 97), "#\\a\n"],
        [("fixnum->char", 122), "#\\z\n"],
        [("fixnum->char", 90), "#\\Z\n"],
        [("fixnum->char", 48), "#\\0\n"],
        [("fixnum->char", 57), "#\\9\n"],
    ],
)
def test_fixnum2char(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("char->fixnum", "A"), "65\n"],
        [("char->fixnum", "a"), "97\n"],
        [("char->fixnum", "z"), "122\n"],
        [("char->fixnum", "Z"), "90\n"],
        [("char->fixnum", "0"), "48\n"],
        [("char->fixnum", "9"), "57\n"],
        [("char->fixnum", ("fixnum->char", 12)), "12\n"],
        [("fixnum->char", ("char->fixnum", "x")), "#\\x\n"],
    ],
)
def test_char2fixnum(program, out, compile_and_run):
    assert compile_and_run(program) == out
