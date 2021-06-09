class Argument:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str(self.value)


## TODO: add validation to the arguments
class Address(Argument):
    def __init__(self, value):
        super().__init__("Address", value)

    def __repr__(self):
        return hex(self.value)


class Constant(Argument):
    def __init__(self, value):
        super().__init__("Constant", value)

    def __repr__(self):
        return hex(self.value)


class Register(Argument):
    def __init__(self, value):
        super().__init__("Register", value)

    def __repr__(self):
        return "V{}".format(hex(self.value))


class Instruction:
    def __init__(self, op_code, mnenomic, args):
        self.op_code = op_code
        self.mnenomic = mnenomic
        self.args = args


class ClearScreen(Instruction):
    def __init__(self, op_code):
        super().__init__(op_code, "CLS", [])


class ReturnFromFunction(Instruction):
    def __init__(self, op_code):
        super().__init__(op_code, "RTN", [])


class CallNativeCode(Instruction):
    def __init__(self, op_code, address):
        super().__init__(op_code, "SYS", [address])


class JumpToAddress(Instruction):
    def __init__(self, op_code, address):
        super().__init__(op_code, "JMP", [address])


class CallFunction(Instruction):
    def __init__(self, op_code, address):
        super().__init__(op_code, "CALL", [address])


class SkipNextInstructionIfEqualsConst(Instruction):
    def __init__(self, op_code, register, const):
        super().__init__(op_code, "SE", [register, const])


class SkipNextInstructionIfNotEqualsConst(Instruction):
    def __init__(self, op_code, register, const):
        super().__init__(op_code, "SNE", [register, const])


class SkipNextInstructionIfRegistersEqual(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "SRE", [reg1, reg2])


class LoadConstantIntoRegister(Instruction):
    def __init__(self, op_code, register, const):
        super().__init__(op_code, "LD", [register, const])


class AddConstantToRegister(Instruction):
    def __init__(self, op_code, register, const):
        super().__init__(op_code, "ADD", [register, const])


class InstructionMatcher:
    def __init__(self):
        pass

    def matches_op_code(self, op_code):
        return False

    def from_op_code(self, op_code):
        raise NotImplementedError()

    def from_assembly_instruction(self, mnemonic, args):
        raise NotImplementedError()


class ClearScreenMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return int.from_bytes(op_code, "big") == 0x00E0

    def from_op_code(self, op_code):
        return ClearScreen(op_code)


class ReturnFromFunctionMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return int.from_bytes(op_code, "big") == 0x00EE

    def from_op_code(self, op_code):
        return ReturnFromFunction(op_code)


class CallNativeCodeMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x00

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return CallNativeCode(op_code, address)


class JumpToAddressMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x10

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return JumpToAddress(op_code, address)


class CallFunctionMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x20

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return CallFunction(op_code, address)


class SkipNextInstructionIfEqualsConstMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x30

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return SkipNextInstructionIfEqualsConst(op_code, register, const)


class SkipNextInstructionIfNotEqualsConstMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x40

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return SkipNextInstructionIfNotEqualsConst(op_code, register, const)


class SkipNextInstructionIfRegistersEqualMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x50
        # the spec actually expects this op code to end with a 0 -> e.g. 0x5XY0, but I'm going to allow any kind of value in the last nibble (which might be out of spec)

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return SkipNextInstructionIfRegistersEqual(op_code, reg1, reg2)


class LoadConstantIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x60

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return LoadConstantIntoRegister(op_code, register, const)


class AddConstantToRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x70

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return AddConstantToRegister(op_code, register, const)


MATCHERS = [
    ClearScreenMatcher(),
    ReturnFromFunctionMatcher(),
    CallNativeCodeMatcher(),  # this must be after the CLS/RTN matchers as it has kind of a greedy matching pattern
    JumpToAddressMatcher(),
    CallFunctionMatcher(),
    SkipNextInstructionIfEqualsConstMatcher(),
    SkipNextInstructionIfNotEqualsConstMatcher(),
    SkipNextInstructionIfRegistersEqualMatcher(),
    LoadConstantIntoRegisterMatcher(),
    AddConstantToRegisterMatcher(),
]
