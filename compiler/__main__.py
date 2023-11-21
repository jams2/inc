import os
import pathlib
import subprocess
import sys
import tempfile

from compiler import *

project_dir = pathlib.Path(__file__).parent.parent


if len(sys.argv) == 2 and sys.argv[1] in ("-p", "--print-asm"):
    emit_program(
        eval(sys.stdin.read().replace("\n", "").replace("\r", "")),
        StdoutWriter().write,
    )
else:
    sys.modules[__name__].__dict__.update({c: Var(c) for c in ("x", "y", "t")})
    with tempfile.TemporaryDirectory() as tmpdirname:
        asmfile = os.path.join(tmpdirname, "stst.s")
        binfile = os.path.join(tmpdirname, "stst")
        runtimefile = project_dir / "startup.c"
        with Writer(asmfile) as writer:
            emit_program(
                eval(sys.stdin.read().replace("\n", "").replace("\r", "")),
                writer.write,
            )
        subprocess.run(
            ["gcc", "-fomit-frame-pointer", runtimefile, asmfile, "-o", binfile],
            check=True,
        )
        print(
            ">",
            subprocess.run([binfile], check=True, capture_output=True).stdout.decode(
                "utf-8"
            ),
            end="",
        )
