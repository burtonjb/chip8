class Argument:
    def __init__(self, name, value, rep):
        self.name = name
        self.value = value

def address(value):
    return Argument("Address", value, lambda x: str(x.value))

def constant(value):
    return Argument("Constant", value, lambda x: str(x.value))

def register(value):
    return Argument("Register", value, lambda x: 'V{}'.format(x.value))

class Instruction:
    def __init__(self, op_code, nemonic, args):
        self.op_code = op_code
        self.nemonic = nemonic
        self.args = args

