import argparse
import os
import pathlib
import subprocess
import sys
import tempfile

from compiler import *

project_dir = pathlib.Path(__file__).parent.parent

builtins = {
    "λ": "lambda",
    "letrec": "letrec",
    "app": "app",
    "f": "f",
    "g": "g",
    **{c: Var(c) for c in ("x", "y", "t")},
}

sys.modules[__name__].__dict__.update(builtins)


parser = argparse.ArgumentParser(prog="compiler")
output_group = parser.add_mutually_exclusive_group(required=True)
output_group.add_argument(
    "-x",
    "--execute",
    required=False,
    default=True,
    action="store_true",
    help="compile and execute program",
)
output_group.add_argument(
    "-p", "--print", required=False, action="store_true", help="print listing"
)
input_group = parser.add_mutually_exclusive_group(required=True)
input_group.add_argument(
    "-f", "--file", required=False, type=str, help="source file path"
)
input_group.add_argument(
    "-i",
    "--read-stdin",
    required=False,
    action="store_true",
    dest="read_stdin",
    help="read from stdin",
)


def main():
    args = parser.parse_args()
    if args.read_stdin:
        program = sys.stdin.read().replace("\n", "").replace("\r", "")
    else:
        with open(args.file, "r") as f:
            program = f.read()

    if args.print:
        emit_program(eval(program), StdoutWriter().write)
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            asmfile = os.path.join(tmpdirname, "stst.s")
            binfile = os.path.join(tmpdirname, "stst")
            runtimefile = project_dir / "startup.c"
            with Writer(asmfile) as writer:
                emit_program(
                    eval(program),
                    writer.write,
                )
            subprocess.run(
                ["gcc", "-fomit-frame-pointer", runtimefile, asmfile, "-o", binfile],
                check=True,
            )
            print(
                ">",
                subprocess.run(
                    [binfile], check=True, capture_output=True
                ).stdout.decode("utf-8"),
                end="",
            )


if __name__ == "__main__":
    main()
