import string
import sys


class Line:
    def __init__(self, text="", indent=4 * " "):
        self.text = text
        self.indent = indent

    def __str__(self):
        return f"{self.text}\n"

    def __rshift__(self, other):
        if isinstance(other, int):
            return self.__class__(f"{other * self.indent}{self.text}")
        else:
            raise TypeError(
                f"__rshift__ not supported between {type(self)} and {type(other)}"
            )

    def __rrshift__(self, other):
        return self >> other

    def __floordiv__(self, other):
        if self.text:
            return self.__class__(f"{self.text}  # {other}")
        # Empty line
        return self.__class__(f"# {other}")


class StdoutWriter:
    def write(self, text):
        sys.stdout.write(str(text))

    def flush(self):
        sys.stdout.flush()


class Writer:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def write(self, text):
        self.file.write(str(text))

    def flush(self):
        self.file.flush()

    def __enter__(self):
        self.file = open(self.filename, "w")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
        self.file.close()


class Label:
    counter = -1

    @classmethod
    def unique(cls):
        cls.counter += 1
        return f"L_{cls.counter}"

    @classmethod
    def _reset(cls):
        cls.counter = -1


###
# Masks                 Tags
# fixnum: | 00000011 |  00000000
# bool:   | 10111111 |
# char:   | 00111111 |  00001111
#         |          |
# Values  |          |
# F       | 00101111 |
# T       | 01101111 |
# null    | 00111111 |
###

FXSHIFT = 2
FXMASK = 0x03
FXTAG = 0x00
BOOL_F = 0x2F
BOOL_T = 0x6F
BOOL_BIT = 6
BOOL_MASK = 0xBF  # BOOL_MASK & (T or F) give F. Doesn't clash with null
NULL = 0x3F
WORDSIZE = 4  # bytes

FIXNUM_BITS = WORDSIZE * 8 - FXSHIFT
FXLOWER = -(2 ** (FIXNUM_BITS - 1))
FXUPPER = (2 ** (FIXNUM_BITS - 1)) - 1

CHARS = string.ascii_letters + string.punctuation + string.whitespace + string.digits
CHARSHIFT = 8
CHARTAG = 0x0F
CHARMASK = 0x3F

PRIMITIVES = {}
PREDICATES = set()


def scheme_name(name):
    def decorator(f):
        f._scheme_name = name
        return f

    return decorator


def primitive(f):
    PRIMITIVES.update(
        {
            f._scheme_name: {
                "nargs": f.__code__.co_argcount - 1,
                "emitter": f,
            }
        }
    )
    return f


def predicate(f):
    PREDICATES.add(f._scheme_name)
    return f


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
        case (rator, *_):
            return rator in PRIMITIVES
        case _:
            return False


def is_if(x):
    match x:
        case ("if", _, _, _):
            return True
        case _:
            return False


def is_and(x):
    match x:
        case ("and", *_):
            return True
        case _:
            return False


def is_or(x):
    match x:
        case ("or", *_):
            return True
        case _:
            return False


def emit_program(p, emit):
    emit_function_header("scheme_entry", emit)
    emit_expr(p, emit)
    emit(1 >> Line("ret"))


def emit_function_header(name, emit):
    emit(1 >> Line(".text"))
    emit(Line(f".globl {name}"))
    emit(1 >> Line(f".type {name}, @function"))
    emit(Line(f"{name}:"))


def emit_expr(expr, emit):
    if is_immediate(expr):
        emit_immediate(expr, emit)
    elif is_primcall(expr):
        emit_primcall(expr, emit)
    elif is_if(expr):
        emit_if(expr, emit)
    elif is_and(expr):
        emit_expr(desugar_and(expr), emit)
    elif is_or(expr):
        emit_expr(desugar_or(expr), emit)
    else:
        raise ValueError(f"Unknown expression: {expr}")


def emit_immediate(x, emit):
    emit(1 >> Line(f"movl ${immediate_rep(x)}, %eax"))


def emit_primcall(x, emit):
    primitive = PRIMITIVES[x[0]]
    if len(x[1:]) != primitive["nargs"]:
        raise TypeError(f"{x[0]}: wrong number of args")
    return primitive["emitter"](*x[1:], emit)


@primitive
@scheme_name("fxadd1")
def emit_fxadd1(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"addl ${immediate_rep(1)}, %eax"))


@primitive
@scheme_name("fxsub1")
def emit_fxsub1(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"subl ${immediate_rep(1)}, %eax"))


@primitive
@scheme_name("fixnum->char")
def emit_fixnum2char(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"shll ${CHARSHIFT - FXSHIFT}, %eax"))
    emit(1 >> Line(f"orl ${CHARTAG}, %eax"))


@primitive
@scheme_name("char->fixnum")
def emit_char2fixnum(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"shrl ${CHARSHIFT - FXSHIFT}, %eax"))


def emit_boolcmp(emit):
    emit(1 >> Line("sete %al") // "set al to 1 if last cmp was equal else 0")
    emit(1 >> Line("movzbl %al, %eax") // "extend al to fill eax")
    emit(
        1
        >> Line(f"sal ${BOOL_BIT}, %al")
        // "shift the result to the bit which discriminates T/F"
    )
    emit(
        1
        >> Line(f"or ${BOOL_F}, %al")
        // "fill the preceding bits with the common bool bits"
    )


@predicate
@primitive
@scheme_name("null?")
def emit_nullp(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"cmp ${NULL}, %eax"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("fixnum?")
def emit_fixnump(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"and ${FXMASK}, %eax"))
    emit(1 >> Line(f"cmp ${FXTAG}, %eax"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("fxzero?")
def emit_fxzerop(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"cmp ${FXTAG}, %eax") // "0 is all zeros")
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("boolean?")
def emit_booleanp(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"and ${BOOL_MASK}, %al") // "F & F and F & T both evaluate to F")
    emit(1 >> Line(f"cmp ${BOOL_F}, %al"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("char?")
def emit_charp(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"and ${CHARMASK}, %al"))
    emit(1 >> Line(f"cmp ${CHARTAG}, %al"))
    emit_boolcmp(emit)


@primitive
@scheme_name("not")
def emit_not(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line(f"cmp ${BOOL_F}, %al"))
    emit_boolcmp(emit)


@primitive
@scheme_name("fxlognot")
def emit_fxlognot(arg, emit):
    emit_expr(arg, emit)
    emit(1 >> Line("not %eax"))
    emit(1 >> Line("and $0xFC, %al") // "reset the tag bits")


def emit_if(program, emit):
    _, test, consequent, alternative = program
    alt_label = Label.unique()
    end_label = Label.unique()
    emit(Line() // f"begin if {alt_label} {end_label}")
    emit_expr(test, emit)
    emit(1 >> Line(f"cmp ${BOOL_F}, %al") // "compare result of test to False")
    emit(1 >> Line(f"je {alt_label}") // "jump to alt if False")
    emit_expr(consequent, emit)
    emit(1 >> Line(f"jmp {end_label}"))
    emit(Line(f"{alt_label}:"))
    emit_expr(alternative, emit)
    emit(Line(f"{end_label}:"))
    emit(Line() // f"end if {alt_label} {end_label}")


def desugar_and(expr):
    match expr:
        case ["and"]:
            return True
        case ["and", rator]:
            return rator
        case ["and", rator, *rest]:
            return ("if", rator, desugar_and(["and", *rest]), False)


def desugar_or(expr):
    match expr:
        case ["or"]:
            return False
        case ["or", rator]:
            return rator
        case ["or", rator, *rest]:
            return ("if", rator, rator, desugar_or(["or", *rest]))
