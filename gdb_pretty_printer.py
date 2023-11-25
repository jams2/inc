import string

import gdb

CHARS = string.ascii_letters + string.punctuation + string.whitespace + string.digits
CHARSHIFT = 8
CHARTAG = 0x0F
CHARMASK = 0x3F

chars = {(ord(c) << CHARSHIFT) | CHARTAG for c in CHARS}


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
        elif (self.val & CHARMASK) == CHARTAG:
            return chr(self.val >> CHARSHIFT)


def custom_value_lookup_function(val):
    if (
        val.type.strip_typedefs().code == gdb.TYPE_CODE_INT
        and val.type.sizeof == 8
        and val in (0x2F, 0x6F, 0x3F, *chars)
    ):
        return CustomValuePrinter(val)
    return None


gdb.pretty_printers.append(custom_value_lookup_function)
