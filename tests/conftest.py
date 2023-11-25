import subprocess
from pathlib import Path

import pytest

from compiler import emit_program
from compiler.io import FileWriter


@pytest.fixture()
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture()
def compile_and_run(tmp_path, project_root):
    def _compile_and_run(program):
        startup = project_root / "startup.c"
        asm_file = tmp_path / "program.s"
        binary = tmp_path / "test"
        with FileWriter(asm_file) as writer:
            emit_program(program, writer.write)

        subprocess.run(
            ["gcc", "-fomit-frame-pointer", startup, asm_file, "-o", binary],
            check=True,
        )
        return subprocess.run([binary], check=True, capture_output=True).stdout.decode(
            "utf-8"
        )

    return _compile_and_run
