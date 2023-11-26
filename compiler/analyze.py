from functools import reduce

from compiler.var import Var


def with_counter(f):
    counter = -1

    def wrapper():
        nonlocal counter
        counter = counter + 1
        return f(counter)

    return wrapper


@with_counter
def get_label(i):
    return f"f{i}"


class composable:
    def __init__(self, f, *rest):
        self.fs = [f, *rest]

    def __ge__(self, other):
        return type(self)(*self.fs, other)

    def __call__(self, arg):
        return reduce(lambda result, f: f(result), self.fs, arg)


@composable
def annotate_freevars(expr):
    match expr:
        case ("lambda", args, body):
            return (
                "lambda",
                args,
                find_freevars(body, set(args)),
                annotate_freevars(body),
            )
        case (first, *rest):
            return type(expr)([annotate_freevars(first), *annotate_freevars(rest)])
        case atom:
            return atom


def find_freevars(expr, env):
    match expr:
        case Var(_) as v:
            return [] if v in env else [v]
        case ("let", binders, body) | ("let*", binders, body):
            return find_freevars(body, {*map(lambda x: x[0], binders), *env})
        case ("lambda", args, body):
            return find_freevars(body, {*args, *env})
        case (first, *rest) if first != "lambda":
            return [*find_freevars(first, env), *find_freevars(rest, env)]
        case _:
            return []


@composable
def convert_closures(expr):
    def _convert_closures(expr):
        match expr:
            case ("lambda", args, freevars, body):
                p, labels = _convert_closures(body)
                label = get_label()
                return ("closure", label, *freevars), [
                    *labels,
                    (label, ("code", args, freevars, p)),
                ]
            case (first, *rest):
                p1, labels = _convert_closures(first)
                p2, labels_2 = _convert_closures(rest)
                return type(expr)((p1, *p2)), [*labels, *labels_2]
            case atom:
                return atom, []

    p, labels = _convert_closures(expr)
    return ["labels", labels, p] if labels else p
