import string
import sys

FXSHIFT = 2
FXMASK = 0x03
BOOL_F = 0x2F
BOOL_T = 0x6F
NULL = 0x3F
WORDSIZE = 4  # bytes

FIXNUM_BITS = WORDSIZE * 8 - FXSHIFT
FXLOWER = -(2 ** (FIXNUM_BITS - 1))
FXUPPER = (2 ** (FIXNUM_BITS - 1)) - 1

CHARS = string.ascii_letters + string.punctuation + string.whitespace + string.digits
CHARSHIFT = 8
CHARTAG = 0x0F

PRIMITIVES = {}


def define_primitive(name):
    def decorator(f):
        PRIMITIVES.update({name: {"nargs": f.__code__.co_argcount - 1, "emitter": f}})
        return f

    return decorator


def is_fixnum(x):
    return not is_bool(x) and isinstance(x, int) and FXLOWER <= x <= FXUPPER


def is_bool(x):
    return x is True or x is False


def is_null(x):
    return x == ()


def is_char(x):
    return isinstance(x, str) and len(x) == 1 and x in CHARS


def is_immediate(x):
    return is_fixnum(x) or is_bool(x) or is_null(x) or is_char(x)


def immediate_rep(x):
    if is_fixnum(x):
        return x << FXSHIFT
    elif is_bool(x):
        return BOOL_T if x else BOOL_F
    elif is_null(x):
        return NULL
    elif is_char(x):
        return (ord(x) << CHARSHIFT) | CHARTAG


def is_primcall(x):
    match x:
        case tuple((rator, *_)):
            return rator in PRIMITIVES
        case _:
            return False


class Line:
    def __init__(self, text, indent=4 * " "):
        self.text = text
        self.indent = indent

    def __str__(self):
        return f"{self.text}\n"

    def __rshift__(self, other):
        return self.__class__(f"{other * self.indent}{self.text}")


class StdoutWriter:
    def write_line(self, line):
        sys.stdout.write(str(line))

    def flush(self):
        sys.stdout.flush()


class Writer:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def write_line(self, line):
        self.file.write(str(line))

    def flush(self):
        self.file.flush()

    def __enter__(self):
        self.file = open(self.filename, "w")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
        self.file.close()


def emit_program(p, writer):
    emit_function_header("scheme_entry", writer)
    emit_expr(p, writer)
    writer.write_line(Line("ret") >> 1)
    writer.flush()


def emit_function_header(name, writer):
    writer.write_line(Line(".text") >> 1)
    writer.write_line(Line(f".globl {name}"))
    writer.write_line(Line(f".type {name}, @function") >> 1)
    writer.write_line(Line(f"{name}:"))


def emit_expr(expr, writer):
    if is_immediate(expr):
        emit_immediate(expr, writer)
    elif is_primcall(expr):
        emit_primcall(expr, writer)
    else:
        raise ValueError(f"Unknown expression: {expr}")


def emit_immediate(x, writer):
    writer.write_line(Line(f"movl ${immediate_rep(x)}, %eax") >> 1)


def emit_primcall(x, writer):
    primitive = PRIMITIVES[x[0]]
    if len(x[1:]) != primitive["nargs"]:
        raise TypeError(f"{x[0]}: wrong number of args")
    return primitive["emitter"](*x[1:], writer)


@define_primitive("fxadd1")
def emit_fxadd1(arg, writer):
    emit_expr(arg, writer)
    writer.write_line(Line(f"addl ${immediate_rep(1)}, %eax") >> 1)


@define_primitive("fxsub1")
def emit_fxsub1(arg, writer):
    emit_expr(arg, writer)
    writer.write_line(Line(f"subl ${immediate_rep(1)}, %eax") >> 1)


@define_primitive("fixnum->char")
def emit_fixnum2char(arg, writer):
    emit_expr(arg, writer)
    writer.write_line(Line(f"shll ${CHARSHIFT - FXSHIFT}, %eax") >> 1)
    writer.write_line(Line(f"orl ${CHARTAG}, %eax") >> 1)


@define_primitive("char->fixnum")
def emit_char2fixnum(arg, writer):
    emit_expr(arg, writer)
    writer.write_line(Line(f"shrl ${CHARSHIFT - FXSHIFT}, %eax") >> 1)
