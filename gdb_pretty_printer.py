import gdb


class CustomValuePrinter:
    """Pretty-printer for custom 64-bit integer values."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        if self.val == 0x2F:
            return "#f"
        elif self.val == 0x6F:
            return "#t"
        elif self.val == 0x3F:
            return "()"


def custom_value_lookup_function(val):
    if (
        val.type.strip_typedefs().code == gdb.TYPE_CODE_INT
        and val.type.sizeof == 8
        and val in (0x2F, 0x6F, 0x3F)
    ):
        return CustomValuePrinter(val)
    return None


gdb.pretty_printers.append(custom_value_lookup_function)
