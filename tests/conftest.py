import subprocess
from pathlib import Path

import pytest

from compiler import Writer, emit_program


@pytest.fixture()
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture()
def compile_and_run(tmp_path, project_root):
    def _compile_and_run(program):
        startup = project_root / "startup.c"
        asm_file = tmp_path / "program.s"
        object_file = tmp_path / "program.o"
        binary = tmp_path / "test"
        with Writer(asm_file) as writer:
            emit_program(program, writer.write)

        subprocess.run(["gcc", "-c", asm_file, "-o", object_file], check=True)
        subprocess.run(["gcc", startup, object_file, "-o", binary], check=True)
        return subprocess.run([binary], check=True, capture_output=True).stdout.decode(
            "utf-8"
        )

    return _compile_and_run
