import string
from dataclasses import dataclass
from itertools import count

from .io import Line


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
WORDSIZE = 8  # bytes

FIXNUM_BITS = WORDSIZE * 8 - FXSHIFT
FXLOWER = -(2 ** (FIXNUM_BITS - 1))
FXUPPER = (2 ** (FIXNUM_BITS - 1)) - 1

CHARS = string.ascii_letters + string.punctuation + string.whitespace + string.digits
CHARSHIFT = 8
CHARTAG = 0x0F
CHARMASK = 0x3F

PRIMITIVES = {}
PREDICATES = set()


@dataclass
class Var:
    name: str


def next_stack_index(si):
    return si - WORDSIZE


def scheme_name(name):
    def decorator(f):
        f._scheme_name = name
        return f

    return decorator


PRIMCALL_REQUIRED_ARGS = 3


def primitive(f):
    PRIMITIVES.update(
        {
            f._scheme_name: {
                "nargs": f.__code__.co_argcount - PRIMCALL_REQUIRED_ARGS,
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


def is_predicate_call(x):
    match x:
        case (rator, *_):
            return rator in PRIMITIVES and rator in PREDICATES
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


def is_let(x):
    match x:
        case ("let", ([_, _], *_), _):
            return True
        case _:
            return False


def is_let_star(x):
    match x:
        case ("let*", ([_, _], *_), _):
            return True
        case _:
            return False


def is_variable(x):
    return isinstance(x, Var)


def is_letrec(x):
    match x:
        case ["letrec", [*_], _]:
            return True
        case _:
            return False


def is_lambda(x):
    match x:
        case ["lambda", [*_], _]:
            return True
        case _:
            return False


def is_app(x, env):
    match x:
        case [rator, *_]:
            try:
                lookup(rator, env)
                return True
            except KeyError:
                return False
        case _:
            return False


def make_initial_env(vars=None, vals=None):
    vars = vars or ()
    vals = vals or ()
    return [(x[0], x[1]) for x in zip(vars, vals, strict=True)]


def emit_program(p, emit):
    emit_function_header("scheme_entry", emit)
    emit(1 >> Line("movq %rsp, %rcx") // "save the C stack pointer")
    emit(1 >> Line("movq %rdi, %rsp") // "rdi has the stack_base arg")
    emit(1 >> Line("call L_scheme_entry"))
    emit(1 >> Line("movq %rcx, %rsp") // "restore the C stack pointer")
    emit_ret(emit)
    if is_letrec(p):
        emit_letrec(p, emit)
    else:
        emit_scheme_entry(p, make_initial_env(), emit)


def emit_scheme_entry(expr, env, emit):
    emit_function_header("L_scheme_entry", emit)
    emit_expr(-WORDSIZE, env, expr, tail=True, emit=emit)


def emit_function_header(name, emit, comment=""):
    emit(1 >> Line(".text"))
    emit(Line(f".globl {name}"))
    emit(1 >> Line(f".type {name}, @function"))
    emit(Line(f"{name}:") // comment)


def emit_expr(si, env, expr, tail, emit):
    if is_immediate(expr):
        emit_immediate(expr, emit)
        emit_ret_when(tail, emit)
    elif is_variable(expr):
        emit_variable_ref(env, expr, emit)
        emit_ret_when(tail, emit)
    elif is_primcall(expr):
        emit_primcall(si, env, expr, emit)
        emit_ret_when(tail, emit)
    elif is_if(expr):
        emit_if(si, env, expr, tail=tail, emit=emit)
    elif is_and(expr):
        emit_expr(si, env, desugar_and(expr), tail=tail, emit=emit)
    elif is_or(expr):
        emit_expr(si, env, desugar_or(expr), tail=tail, emit=emit)
    elif is_let(expr):
        emit_let(si, env, expr, tail=tail, emit=emit)
    elif is_let_star(expr):
        emit_let_star(si, env, expr, tail=tail, emit=emit)
    elif is_app(expr, env):
        emit_app(si, env, expr, tail=tail, emit=emit)
    else:
        raise ValueError(f"Unknown expression: {expr}")


def emit_immediate(x, emit):
    emit(1 >> Line(f"movq ${immediate_rep(x)}, %rax"))


def emit_primcall(si, env, x, emit):
    primitive = PRIMITIVES[x[0]]
    if len(x[1:]) != primitive["nargs"]:
        raise TypeError(f"{x[0]}: wrong number of args")
    emit(1 >> Line() // f"begin {x[0]}")
    primitive["emitter"](si, env, *x[1:], emit)
    emit(1 >> Line() // f"end {x[0]}")


@primitive
@scheme_name("fxadd1")
def emit_fxadd1(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"addq ${immediate_rep(1)}, %rax"))


@primitive
@scheme_name("fxsub1")
def emit_fxsub1(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"subq ${immediate_rep(1)}, %rax"))


@primitive
@scheme_name("fixnum->char")
def emit_fixnum2char(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"shlq ${CHARSHIFT - FXSHIFT}, %rax"))
    emit(1 >> Line(f"orq ${CHARTAG}, %rax"))


@primitive
@scheme_name("char->fixnum")
def emit_char2fixnum(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"shrq ${CHARSHIFT - FXSHIFT}, %rax"))


def emit_boolcmp(emit, cmp="e"):
    emit(1 >> Line(f"set{cmp} %al"))
    emit(1 >> Line("movzbq %al, %rax") // "extend al to fill rax")
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
def emit_nullp(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"cmp ${NULL}, %rax"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("fixnum?")
def emit_fixnump(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"andq ${FXMASK}, %rax"))
    emit(1 >> Line(f"cmp ${FXTAG}, %rax"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("fxzero?")
def emit_fxzerop(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"cmp ${FXTAG}, %rax") // "0 is all zeros")
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("boolean?")
def emit_booleanp(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"and ${BOOL_MASK}, %al") // "F & F and F & T both evaluate to F")
    emit(1 >> Line(f"cmp ${BOOL_F}, %al"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("char?")
def emit_charp(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"and ${CHARMASK}, %al"))
    emit(1 >> Line(f"cmp ${CHARTAG}, %al"))
    emit_boolcmp(emit)


@primitive
@scheme_name("not")
def emit_not(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line(f"cmp ${BOOL_F}, %al"))
    emit_boolcmp(emit)


@primitive
@scheme_name("fxlognot")
def emit_fxlognot(si, env, arg, emit):
    emit_expr(si, env, arg, tail=False, emit=emit)
    emit(1 >> Line("not %rax"))
    emit(1 >> Line("and $0xFC, %al") // "reset the tag bits")


def emit_if(si, env, program, tail, emit):
    _, test, consequent, alternative = program
    alt_label = Label.unique()
    end_label = Label.unique()
    emit(Line() // f"begin if {alt_label} {end_label}")
    # TODO: (if (fxzero? e0) conseq alt) causes an extra comparison,
    # and extra work creating a #t or #f value that we don't use
    # write the test
    emit_expr(si, env, test, tail=False, emit=emit)

    # write the consequent
    emit(1 >> Line(f"cmp ${BOOL_F}, %al") // "compare result of test to False")
    emit(1 >> Line(f"je {alt_label}") // "jump to alt if False")
    emit_expr(si, env, consequent, tail=tail, emit=emit)
    if not tail:
        # if this expression is in tail position the sub-expressions
        # will eventually return so we don't need the end label
        emit(1 >> Line(f"jmp {end_label}"))

    # write the alternative
    emit(Line(f"{alt_label}:"))
    emit_expr(si, env, alternative, tail=tail, emit=emit)

    if not tail:
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


def emit_binargs(si, env, arg1, arg2, emit):
    """
    eval arg1 and arg2.

    arg1 result will be in <si>(%rsp), arg2 in %rax
    """
    emit_expr(si, env, arg1, tail=False, emit=emit)
    emit_stack_save(si, emit)
    emit_expr(next_stack_index(si), env, arg2, tail=False, emit=emit)


def emit_stack_save(si, emit, source="rax", comment="stack save"):
    emit(1 >> Line(f"movq %{source}, {si}(%rsp)") // comment)


def emit_stack_load(si, emit, dest="rax", comment=""):
    emit(1 >> Line(f"movq {si}(%rsp), %{dest}") // comment)


@primitive
@scheme_name("fx+")
def emit_fxplus(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"addq {si}(%rsp), %rax"))


@primitive
@scheme_name("fx-")
def emit_fxminus(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"subq %rax, {si}(%rsp)"))
    emit_stack_load(si, emit)


@primitive
@scheme_name("fx*")
def emit_fxmul(si, env, arg1, arg2, emit):
    """
    Input numbers are scaled by 4. This means multiplication is really
    4x * 4y = 16xy, where we want 4x * 4y = 4xy.

    Thus we implement multiplication as 4xy = (4x / 4) * 4y, using sarq to
    implement the division.
    """
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"sarq ${FXSHIFT}, {si}(%rsp)"))
    emit(1 >> Line(f"imulq {si}(%rsp), %rax"))


@primitive
@scheme_name("fxlogand")
def emit_fxlogand(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"andq {si}(%rsp), %rax"))


@primitive
@scheme_name("fxlogor")
def emit_fxlogor(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"orq {si}(%rsp), %rax"))


@predicate
@primitive
@scheme_name("fx=")
def emit_fxequal(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"cmpq {si}(%rsp), %rax"))
    emit_boolcmp(emit)


@predicate
@primitive
@scheme_name("fx<")
def emit_fxlt(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"cmpq %rax, {si}(%rsp)"))
    emit_boolcmp(emit, "l")


@predicate
@primitive
@scheme_name("fx<=")
def emit_fxlte(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"cmpq %rax, {si}(%rsp)"))
    emit_boolcmp(emit, "le")


@predicate
@primitive
@scheme_name("fx>")
def emit_fxgt(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"cmpq %rax, {si}(%rsp)"))
    emit_boolcmp(emit, "g")


@predicate
@primitive
@scheme_name("fx>=")
def emit_fxgte(si, env, arg1, arg2, emit):
    emit_binargs(si, env, arg1, arg2, emit)
    emit(1 >> Line(f"cmpq %rax, {si}(%rsp)"))
    emit_boolcmp(emit, "ge")


@predicate
@primitive
@scheme_name("char=")
def emit_charequal(si, env, arg1, arg2, emit):
    emit_fxequal(si, env, arg1, arg2, emit)


@predicate
@primitive
@scheme_name("char<")
def emit_charlt(si, env, arg1, arg2, emit):
    emit_fxlt(si, env, arg1, arg2, emit)


@predicate
@primitive
@scheme_name("char<=")
def emit_charlte(si, env, arg1, arg2, emit):
    emit_fxlte(si, env, arg1, arg2, emit)


@predicate
@primitive
@scheme_name("char>")
def emit_chargt(si, env, arg1, arg2, emit):
    emit_fxgt(si, env, arg1, arg2, emit)


@predicate
@primitive
@scheme_name("char>=")
def emit_chargte(si, env, arg1, arg2, emit):
    emit_fxgte(si, env, arg1, arg2, emit)


def emit_let(si, env, expr, tail, emit):
    def process_let(bindings, si, new_env):
        match bindings:
            case []:
                return emit_expr(si, new_env, expr[2], tail=tail, emit=emit)
            case [(lhs, rhs), *rest]:
                if not isinstance(lhs, Var):
                    raise ValueError("lhs of let binding must be a Var")
                emit_expr(si, env, rhs, tail=False, emit=emit)
                emit_stack_save(si, emit, comment=f"let bind {lhs.name}")
                return process_let(
                    rest, next_stack_index(si), extend_env(lhs, si, new_env)
                )

    return process_let(expr[1], si, env)


def emit_let_star(si, env, expr, tail, emit):
    def process_let_star(bindings, si, new_env):
        match bindings:
            case []:
                return emit_expr(si, new_env, expr[2], tail=tail, emit=emit)
            case [(lhs, rhs), *rest]:
                if not isinstance(lhs, Var):
                    raise ValueError("lhs of let binding must be a Var")
                emit_expr(si, new_env, rhs, tail=False, emit=emit)
                emit_stack_save(si, emit)
                return process_let_star(
                    rest, next_stack_index(si), extend_env(lhs, si, new_env)
                )

    return process_let_star(expr[1], si, env)


def extend_env(var, si, env):
    return [(var, si), *env]


def lookup(var, env):
    for x, si in env:
        if x == var:
            return si
    raise KeyError(f"'{var}' not in env: {env!r}")


def emit_variable_ref(env, expr, emit):
    if (si := lookup(expr, env)) is not None:
        emit_stack_load(si, emit, comment=f"lookup {expr.name}")
    else:
        raise LookupError(f"Unbound {expr}")


def emit_letrec(expr, emit):
    _, bindings, body = expr
    lvars = [x[0] for x in bindings]
    lambdas = [x[1] for x in bindings]
    labels = [Label.unique() for _ in lvars]
    env = make_initial_env(lvars, labels)
    for lvar, lam, label in zip(lvars, lambdas, labels, strict=True):
        emit_lambda(env, lam, label, emit, comment=f"lambda@{lvar}")
    emit_scheme_entry(body, env, emit)


def emit_lambda(env, expr, label, emit, comment=""):
    emit_function_header(label, emit, comment=comment)
    _, formals, body = expr
    si = -WORDSIZE
    for formal, si in zip(formals, count(si, -WORDSIZE)):
        env = extend_env(formal, si, env)
    emit_expr(next_stack_index(si), env, body, tail=True, emit=emit)


def emit_app(si, env, expr, tail, emit):
    def emit_arguments(si, args):
        match args:
            case first, *rest:
                emit_expr(si, env, first, tail=False, emit=emit)
                emit_stack_save(si, emit, comment="save arg on stack")
                return emit_arguments(next_stack_index(si), rest)
            case _:
                return

    rator, *args = expr
    emit(1 >> Line() // f"begin {lookup(rator, env)} ({rator}) prologue")
    emit_arguments(
        next_stack_index(si),  # leave one cell empty for the return address
        args,
    )
    if tail:
        # shift the args from (si + WORDSIZE)... down to -WORDSIZE(%rsp)...
        emit(1 >> Line() // "begin TCO")
        for i in range(1, len(args) + 1):
            emit(1 >> Line() // f"shift arg {i} to local {i} position")
            emit(1 >> Line(f"movq {si - i * WORDSIZE}(%rsp), %rax"))
            emit(1 >> Line(f"movq %rax, {-i * WORDSIZE}(%rsp)"))
        emit(1 >> Line(f"jmp {lookup(rator, env)}") // "end TCO")
    else:
        # adjust rsp so call puts the return address in the empty cell
        emit_adjust_base(si + WORDSIZE, emit)
        emit_call(lookup(rator, env), emit)
        emit_adjust_base(-(si + WORDSIZE), emit)


def emit_adjust_base(offset, emit):
    if offset > 0:
        emit(1 >> Line(f"add ${offset}, %rsp"))
    elif offset < 0:
        emit(1 >> Line(f"sub ${-offset}, %rsp"))


def emit_call(label, emit):
    emit(1 >> Line(f"call {label}"))


def emit_ret_when(cond, emit):
    if cond:
        emit_ret(emit)


def emit_ret(emit):
    emit(1 >> Line("ret"))
