import sys


FXSHIFT = 2
FXMASK = 0x03
BOOL_F = 0x2F
BOOL_T = 0x6F
WORDSIZE = 8  # bytes

FIXNUM_BITS = WORDSIZE * 8 - FXSHIFT


def is_int(value):
    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False


def check_int(value):
    if value < -(2**61) or value > 2**61 - 1:
        raise ValueError("fixnum is implemented as a 64 bit signed integer")


def emit_program(p, out=sys.stdout):
    if not is_int(p):
        raise ValueError("Invalid program")
    check_int(p)
    asm = f"""
    .text
.globl scheme_entry
    .type scheme_entry, @function
scheme_entry:
    movl    ${p}, %eax
    ret
    """
    out.write(asm)
    out.flush()
