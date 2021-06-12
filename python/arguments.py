class Argument:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, o):
        if not type(o) == type(self):
            return False
        return o.name == self.name and o.value == self.value


## TODO: add validation to the arguments
class Raw(Argument):  # 4 nibble value (16 bits)
    def __init__(self, value):
        super().__init__("Raw", value)

    def __repr__(self):
        return "r%#x" % self.value


class Address(Argument):  # 3 nibble value (12 bits)
    def __init__(self, value):
        super().__init__("Address", value)

    def __repr__(self):
        return "a%#x" % self.value


class Constant(Argument):  # 2 nibble value (1 byte or 8 bits)
    def __init__(self, value):
        super().__init__("Constant", value)

    def __repr__(self):
        return "c%#x" % self.value


class Nibble(Argument):  # 1 nibble value (4 bits, half a byte)
    def __init__(self, value):
        super().__init__("Nibble", value)

    def __repr__(self):
        return "n%#x" % self.value


class Register(Argument):
    def __init__(self, value):
        super().__init__("Register", value)

    def __repr__(self):
        return "v%#x" % self.value


class AsmParser:
    """
    Parses an argument of form tNNN, where t is a character representing the type and NNN is a integer, into an "argument" object
    """

    @staticmethod
    def parse_asm(asm):
        split = asm.split()
        if len(split) > 1:
            inst, args = split[0].strip(), split[1:]
            return inst, AsmParser.parse_args(args)
        elif len(split) == 1:
            return split[0].strip(), []
        else:
            return

    @staticmethod
    def parse_args(args):
        parsed_args = [AsmParser.parse_argument(arg) for arg in args]
        return [arg for arg in parsed_args if arg is not None]

    @staticmethod
    def parse_argument(string):
        string = string.lower()
        if string[0] == "a":
            return Address(int(string[1:], base=16))
        elif string[0] == "c":
            return Constant(int(string[1:], base=16))
        elif string[0] == "n":
            return Nibble(int(string[1:], base=16))
        elif string[0] == "v":
            return Register(int(string[1:], base=16))
        elif string[0] == "r":
            return Raw(int(string[1:], base=16))
        else:
            return None
