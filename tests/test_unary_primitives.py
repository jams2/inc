import pytest


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
        [("fxsub1", 2305843009213693951), "2305843009213693950\n"],
        [("fxsub1", -2305843009213693950), "-2305843009213693951\n"],
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


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("null?", ()), "#t\n"],
        [("null?", False), "#f\n"],
        [("null?", True), "#f\n"],
        [("null?", ("null?", ())), "#f\n"],
        [("null?", "a"), "#f\n"],
        [("null?", 0), "#f\n"],
        [("null?", -10), "#f\n"],
        [("null?", 10), "#f\n"],
    ],
)
def test_nullp(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fixnum?", 0), "#t\n"],
        [("fixnum?", 1), "#t\n"],
        [("fixnum?", -1), "#t\n"],
        [("fixnum?", 37287), "#t\n"],
        [("fixnum?", -23873), "#t\n"],
        [("fixnum?", 536870911), "#t\n"],
        [("fixnum?", -536870912), "#t\n"],
        [("fixnum?", True), "#f\n"],
        [("fixnum?", False), "#f\n"],
        [("fixnum?", ()), "#f\n"],
        [("fixnum?", "Q"), "#f\n"],
        [("fixnum?", ("fixnum?", 12)), "#f\n"],
        [("fixnum?", ("fixnum?", False)), "#f\n"],
        [("fixnum?", ("fixnum?", "A")), "#f\n"],
        [("fixnum?", ("char->fixnum", "r")), "#t\n"],
        [("fixnum?", ("fixnum->char", 12)), "#f\n"],
    ],
)
def test_fixnump(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxzero?", 0), "#t\n"],
        [("fxzero?", 1), "#f\n"],
        [("fxzero?", -1), "#f\n"],
        [("fxzero?", 64), "#f\n"],
        [("fxzero?", 960), "#f\n"],
    ],
)
def test_fxzerop(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("boolean?", True), "#t\n"],
        [("boolean?", False), "#t\n"],
        [("boolean?", 0), "#f\n"],
        [("boolean?", 1), "#f\n"],
        [("boolean?", -1), "#f\n"],
        [("boolean?", ()), "#f\n"],
        [("boolean?", "a"), "#f\n"],
        [("boolean?", ("boolean?", 0)), "#t\n"],
        [("boolean?", ("fixnum?", ("boolean?", 0))), "#t\n"],
    ],
)
def test_booleanp(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("char?", "a"), "#t\n"],
        [("char?", "Z"), "#t\n"],
        [("char?", "\n"), "#t\n"],
        [("char?", True), "#f\n"],
        [("char?", False), "#f\n"],
        [("char?", ()), "#f\n"],
        [("char?", ("char?", True)), "#f\n"],
        [("char?", 0), "#f\n"],
        [("char?", 23870), "#f\n"],
        [("char?", -23789), "#f\n"],
    ],
)
def test_charp(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("not", True), "#f\n"],
        [("not", False), "#t\n"],
        [("not", 15), "#f\n"],
        [("not", ()), "#f\n"],
        [("not", "A"), "#f\n"],
        [("not", ("not", True)), "#t\n"],
        [("not", ("not", False)), "#f\n"],
        [("not", ("not", 15)), "#t\n"],
        [("not", ("fixnum?", 15)), "#f\n"],
        [("not", ("fixnum?", False)), "#t\n"],
    ],
)
def test_not(program, out, compile_and_run):
    assert compile_and_run(program) == out


@pytest.mark.parametrize(
    ("program", "out"),
    [
        [("fxlognot", 0), "-1\n"],
        [("fxlognot", -1), "0\n"],
        [("fxlognot", 1), "-2\n"],
        [("fxlognot", -2), "1\n"],
        [("fxlognot", 536870911), "-536870912\n"],
        [("fxlognot", -536870912), "536870911\n"],
        [("fxlognot", ("fxlognot", 237463)), "237463\n"],
    ],
)
def test_fxlognot(program, out, compile_and_run):
    assert compile_and_run(program) == out
