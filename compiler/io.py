import sys


class Line:
    INDENT = 4 * " "

    def __init__(self, text="", comment="", indents=0):
        self.text = text
        self.comment = comment
        self.indents = indents

    def __str__(self):
        if self.comment:
            if self.text:
                out = f"{self.text}  # {self.comment}\n"
            else:
                out = f"# {self.comment}\n"
        else:
            out = f"{self.text}\n"
        return f"{self.indents * self.INDENT}{out}"

    def __rshift__(self, other):
        if isinstance(other, int):
            return self.__class__(
                self.text,
                comment=self.comment,
                indents=self.indents + other,
            )
        else:
            raise TypeError(
                f"__rshift__ not supported between {type(self)} and {type(other)}"
            )

    def __rrshift__(self, other):
        return self >> other

    def __floordiv__(self, other):
        return self.__class__(
            text=self.text, comment=other, indents=self.indents
        )


class Writer:
    def __init__(self):
        self.lines = []

    def write(self, line: Line):
        self.lines.append(line)


class StdoutWriter(Writer):
    def flush(self):
        for line in self.lines:
            sys.stdout.write(str(line))
        sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()


class FileWriter(Writer):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.file = None

    def flush(self):
        for line in self.lines:
            self.file.write(str(line))
        self.file.flush()

    def __enter__(self):
        self.file = open(self.filename, "w")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
        self.file.close()
