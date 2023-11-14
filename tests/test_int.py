import pytest


@pytest.mark.parametrize(
    ("program", "output"),
    [
        [0, "0\n"],
        [1, "1\n"],
        [-1, "-1\n"],
        [10, "10\n"],
        [-10, "-10\n"],
        [2736, "2736\n"],
        [-2736, "-2736\n"],
        [536870911, "536870911\n"],
        [-536870912, "-536870912\n"],
    ],
)
def test_compile_int(program, output, compile_and_run):
    result = compile_and_run(program)
    assert result == output
