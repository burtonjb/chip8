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


class Instruction:
    def __init__(
        self,
        args,  # list of Argument objects
        op_code=None,  # original op code, from disassembling e.g. 0x00EE
        asm=None,  # e.g. original asm instruction, eg. CALL 0x123
    ):
        self.args = args
        self._op_code = op_code
        self._asm = (
            asm  # these are mostly populated from cowgod's reverse engineered spec, but they may be slightly different
        )

    @property
    def op_code(self):  # computes the op_code from the instruction and args
        if type(self._op_code) == bytes:
            return int.from_bytes(self._op_code, byteorder="big")
        if len(self.args) > 0 and self.args[0]:
            return self.args[0].value
        return self._op_code

    @property
    def asm(self):  # computes the asm string from the instruction and the args
        return "{}\t{}".format(self._asm, "r%#x" % self.op_code)

    def __repr__(self):
        return self.asm

    def __eq__(self, o):
        if not type(o) == type(self):
            return False
        return self.args == o.args


class ClearScreen(Instruction):
    MNEMONIC = "CLS"  # (Applies to everywhere this pattern is used) I would like to make this a constant, but it seems like python doesn't support it out-of-the-box (I think mypy supports it, but I'm not using mypy)

    def __init__(self, op_code=None, asm=None):
        super().__init__([], op_code, asm)

    @property
    def op_code(self):
        return 0x00E0

    @property
    def asm(self):
        return ClearScreen.MNEMONIC


class ReturnFromFunction(Instruction):
    MNEMONIC = "RTN"

    def __init__(self, op_code=None, asm=None):
        super().__init__([], op_code, asm)

    @property
    def op_code(self):
        return 0x00EE

    @property
    def asm(self):
        return ReturnFromFunction.MNEMONIC


class CallNativeCode(Instruction):
    MNEMONIC = "SYS"

    def __init__(self, address, op_code=None, asm=None):
        super().__init__([address], op_code, asm)
        self.address = address

    @property
    def op_code(self):
        return 0x0000 ^ self.address.value

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.address)


class JumpToAddress(Instruction):
    MNEMONIC = "JMP"

    def __init__(self, address, op_code=None, asm=None):
        super().__init__([address], op_code, asm)
        self.address = address

    @property
    def op_code(self):
        return 0x1000 ^ self.address.value

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.address)


class CallFunction(Instruction):
    MNEMONIC = "CALL"

    def __init__(self, address, op_code=None, asm=None):
        super().__init__([address], op_code, asm)
        self.address = address

    @property
    def op_code(self):
        return 0x2000 ^ self.address.value

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.address)


class SkipNextInstructionIfEqualsConst(Instruction):
    MNEMONIC = "SE"

    def __init__(self, register, const, op_code=None, asm=None):
        super().__init__([register, const], op_code, asm)
        self.register = register
        self.const = const

    @property
    def op_code(self):
        return 0x3000 ^ (self.register.value << 8) ^ (self.const.value)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.register, self.const)


class SkipNextInstructionIfNotEqualsConst(Instruction):
    MNEMONIC = "SNE"

    def __init__(self, register, const, op_code=None, asm=None):
        super().__init__([register, const], op_code, asm)
        self.register = register
        self.const = const

    @property
    def op_code(self):
        return 0x4000 ^ (self.register.value << 8) ^ (self.const.value)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.register, self.const)


class SkipNextInstructionIfRegistersEqual(Instruction):
    MNEMONIC = "SRE"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code, asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x5000 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class LoadConstantIntoRegister(Instruction):
    MNEMONIC = "LD"

    def __init__(self, register, const, op_code=None, asm=None):
        super().__init__([register, const], op_code, asm)
        self.register = register
        self.const = const

    @property
    def op_code(self):
        return 0x6000 ^ (self.register.value << 8) ^ (self.const.value)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.register, self.const)


class AddConstantToRegister(Instruction):
    MNEMONIC = "ADD"

    def __init__(self, register, const, op_code=None, asm=None):
        super().__init__([register, const], op_code, asm)
        self.register = register
        self.const = const

    @property
    def op_code(self):
        return 0x7000 ^ (self.register.value << 8) ^ (self.const.value)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.register, self.const)


class LoadRegisterIntoRegister(Instruction):
    MNEMONIC = "LDR"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code, asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8000 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class OrRegisters(Instruction):
    MNEMONIC = "OR"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8001 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class AndRegisters(Instruction):
    MNEMONIC = "AND"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8002 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class XorRegisters(Instruction):
    MNEMONIC = "XOR"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8003 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class AddRegisters(Instruction):
    MNEMONIC = "ADD"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8004 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class SubtractRegisters(Instruction):
    MNEMONIC = "SUB"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8005 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class ShiftRightRegister(Instruction):
    MNEMONIC = "SHR"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = (
            reg2  # from the spec - seems like this is an accepted input, but only reg1 is actually right/left shifted
        )

    @property
    def op_code(self):
        return 0x8006 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class ReverseSubtractRegisters(Instruction):
    MNEMONIC = "SUBN"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x8007 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class ShiftLeftRegister(Instruction):
    MNEMONIC = "SHL"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = (
            reg2  # from the spec - seems like this is an accepted input, but only reg1 is actually right/left shifted
        )

    @property
    def op_code(self):
        return 0x800E ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class SkipNextInstructionIfRegistersNotEquals(Instruction):
    MNEMONIC = "SRNE"

    def __init__(self, reg1, reg2, op_code=None, asm=None):
        super().__init__([reg1, reg2], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2

    @property
    def op_code(self):
        return 0x9000 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg1, self.reg2)


class SetAddressRegister(Instruction):
    MNEMONIC = "LDI"

    def __init__(self, address, op_code=None, asm=None):
        super().__init__([address], op_code=op_code, asm=asm)
        self.address = address

    @property
    def op_code(self):
        return 0xA000 ^ (self.address.value)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.address)


class JumpToAddressPlusV0(Instruction):
    MNEMONIC = "JMPR"

    def __init__(self, address, op_code=None, asm=None):
        super().__init__([address], op_code=op_code, asm=asm)
        self.address = address

    @property
    def op_code(self):
        return 0xB000 ^ (self.address.value)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.address)


class GenerateRandomNumberWithMask(Instruction):
    MNEMONIC = "RNG"

    def __init__(self, register, mask, op_code=None, asm=None):
        super().__init__([register, mask], op_code=op_code, asm=asm)
        self.reg = register
        self.const = mask

    @property
    def op_code(self):
        return 0xC000 ^ (self.reg.value << 8) ^ (self.const.value)

    @property
    def asm(self):
        return "{}\t{} {}".format(self.MNEMONIC, self.reg, self.const)


class DrawSprite(Instruction):
    MNEMONIC = "DRAW"

    def __init__(self, reg1, reg2, nibble, op_code=None, asm=None):
        super().__init__([reg1, reg2, nibble], op_code=op_code, asm=asm)
        self.reg1 = reg1
        self.reg2 = reg2
        self.nibble = nibble

    @property
    def op_code(self):
        return 0xD000 ^ (self.reg1.value << 8) ^ (self.reg2.value << 4) ^ (self.nibble.value)

    @property
    def asm(self):
        return "{}\t{} {} {}".format(self.MNEMONIC, self.reg1, self.reg2, self.nibble)


class SkipIfKeyPressed(Instruction):
    MNEMONIC = "SKP"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xE09E ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class SkipIfKeyNotPressed(Instruction):
    MNEMONIC = "SKNP"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xE0A1 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class LoadDelayTimerIntoRegister(Instruction):
    MNEMONIC = "LDD"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF007 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class WaitForKeyPressLoadIntoRegister(Instruction):
    MNEMONIC = "WKPL"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF00A ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class SetDelayTimer(Instruction):
    MNEMONIC = "SDT"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF015 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class SetSoundTimer(Instruction):
    MNEMONIC = "SST"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF018 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class AddRegisterToAddressRegister(Instruction):
    MNEMONIC = "ADDI"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF01E ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class SetAddressRegisterToSpriteInRegister(Instruction):
    MNEMONIC = "SISR"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF029 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class BCDDecodeRegister(Instruction):
    MNEMONIC = "BCD"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF033 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class StoreRegisters(Instruction):
    MNEMONIC = "STR"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF055 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class ReadRegisters(Instruction):
    MNEMONIC = "LDIR"

    def __init__(self, reg, op_code=None, asm=None):
        super().__init__([reg], op_code=op_code, asm=asm)
        self.reg = reg

    @property
    def op_code(self):
        return 0xF065 ^ (self.reg.value << 8)

    @property
    def asm(self):
        return "{}\t{}".format(self.MNEMONIC, self.reg)


class InstructionMatcher:
    def __init__(self):
        pass

    def matches_op_code(self, op_code):
        raise NotYetImplemented(op_code=op_code)

    def from_op_code(self, op_code):
        raise NotYetImplemented(op_code=op_code)

    def matches_asm(self, asm):
        raise NotYetImplemented(asm=asm)

    def from_asm(self, asm):
        raise NotYetImplemented(asm=asm)


class ClearScreenMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return int.from_bytes(op_code, "big") == 0x00E0

    def from_op_code(self, op_code):
        return ClearScreen(op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == ClearScreen.MNEMONIC and len(args) == 0

    def from_asm(self, asm):
        return ClearScreen(asm=asm)


class ReturnFromFunctionMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return int.from_bytes(op_code, "big") == 0x00EE

    def from_op_code(self, op_code):
        return ReturnFromFunction(op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == ReturnFromFunction.MNEMONIC and len(args) == 0

    def from_asm(self, asm):
        return ReturnFromFunction(asm=asm)


class CallNativeCodeMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x00

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return CallNativeCode(address, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == CallNativeCode.MNEMONIC and len(args) == 1 and type(args[0]) == Address

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return CallNativeCode(args[0], asm=asm)


class JumpToAddressMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x10

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return JumpToAddress(address, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == JumpToAddress.MNEMONIC and len(args) == 1 and type(args[0]) == Address

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return JumpToAddress(args[0], asm=asm)


class CallFunctionMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x20

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return CallFunction(address, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == CallFunction.MNEMONIC and len(args) == 1 and type(args[0]) == Address

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return CallFunction(args[0], asm=asm)


class SkipNextInstructionIfEqualsConstMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x30

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return SkipNextInstructionIfEqualsConst(register, const, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == SkipNextInstructionIfEqualsConst.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Constant
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipNextInstructionIfEqualsConst(args[0], args[1], asm=asm)


class SkipNextInstructionIfNotEqualsConstMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x40

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return SkipNextInstructionIfNotEqualsConst(register, const, op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == SkipNextInstructionIfNotEqualsConst.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Constant
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipNextInstructionIfNotEqualsConst(args[0], args[1], asm=asm)


class SkipNextInstructionIfRegistersEqualMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x50
        # the spec actually expects this op code to end with a 0 -> e.g. 0x5XY0, but I'm going to allow any kind of value in the last nibble (which might be out of spec)

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return SkipNextInstructionIfRegistersEqual(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == SkipNextInstructionIfRegistersEqual.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipNextInstructionIfRegistersEqual(args[0], args[1], asm=asm)


class LoadConstantIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x60

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return LoadConstantIntoRegister(register, const, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == LoadConstantIntoRegister.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Constant
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return LoadConstantIntoRegister(args[0], args[1], asm=asm)


class AddConstantToRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x70

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return AddConstantToRegister(register, const, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == AddConstantToRegister.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Constant
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return AddConstantToRegister(args[0], args[1], asm=asm)


class LoadRegisterIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x00

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return LoadRegisterIntoRegister(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == LoadRegisterIntoRegister.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return LoadRegisterIntoRegister(args[0], args[1], asm=asm)


class OrRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x01

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return OrRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == OrRegisters.MNEMONIC and len(args) == 2 and type(args[0]) == Register and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return OrRegisters(args[0], args[1], asm=asm)


class AndRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x02

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return AndRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == AndRegisters.MNEMONIC and len(args) == 2 and type(args[0]) == Register and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return AndRegisters(args[0], args[1], asm=asm)


class XorRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x03

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return XorRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == XorRegisters.MNEMONIC and len(args) == 2 and type(args[0]) == Register and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return XorRegisters(args[0], args[1], asm=asm)


class AddRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x04

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return AddRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == AddRegisters.MNEMONIC and len(args) == 2 and type(args[0]) == Register and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return AddRegisters(args[0], args[1], asm=asm)


class SubtractRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x05

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return SubtractRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == SubtractRegisters.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SubtractRegisters(args[0], args[1], asm=asm)


class ShiftRightRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x06

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return ShiftRightRegister(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == ShiftRightRegister.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ShiftRightRegister(args[0], args[1], asm=asm)


class ReverseSubtractRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x07

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return ReverseSubtractRegisters(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == ReverseSubtractRegisters.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ReverseSubtractRegisters(args[0], args[1], asm=asm)


class ShiftLeftRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x0E

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return ShiftLeftRegister(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == ShiftLeftRegister.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ShiftLeftRegister(args[0], args[1], asm=asm)


class SkipNextInstructionIfRegistersNotEqualsMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x90
        # the spec actually expects this op code to end with a 0 -> e.g. 0x5XY0, but I'm going to allow any kind of value in the last nibble (which might be out of spec)
        # at least I'm being consistently overly permissive

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        return SkipNextInstructionIfRegistersNotEquals(reg1, reg2, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == SkipNextInstructionIfRegistersNotEquals.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Register
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipNextInstructionIfRegistersNotEquals(args[0], args[1], asm=asm)


class SetAddressRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xA0

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return SetAddressRegister(address, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SetAddressRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Address

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SetAddressRegister(args[0], asm=asm)


class JumpToAddressPlusV0Matcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xB0

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return JumpToAddressPlusV0(address, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == JumpToAddressPlusV0.MNEMONIC and len(args) == 1 and type(args[0]) == Address

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return JumpToAddressPlusV0(args[0], asm=asm)


class GenerateRandomNumberWithMaskMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xC0

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return GenerateRandomNumberWithMask(register, const, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == GenerateRandomNumberWithMask.MNEMONIC
            and len(args) == 2
            and type(args[0]) == Register
            and type(args[1]) == Constant
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return GenerateRandomNumberWithMask(args[0], args[1], asm=asm)


class DrawSpriteMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xD0

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register((op_code[1] & 0xF0) >> 4)
        nibble = Nibble(op_code[1] & 0x0F)
        return DrawSprite(reg1, reg2, nibble, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return (
            ins == DrawSprite.MNEMONIC
            and len(args) == 3
            and type(args[0]) == Register
            and type(args[1]) == Register
            and type(args[2]) == Nibble
        )

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return DrawSprite(args[0], args[1], args[2], asm=asm)


class SkipIfKeyPressedMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xE0 and (op_code[1] & 0xFF) == 0x9E

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SkipIfKeyPressed(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SkipIfKeyPressed.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipIfKeyPressed(args[0], asm=asm)


class SkipIfKeyNotPressedMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xE0 and (op_code[1] & 0xFF) == 0xA1

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SkipIfKeyNotPressed(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SkipIfKeyNotPressed.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SkipIfKeyNotPressed(args[0], asm=asm)


class LoadDelayTimerIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x07

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return LoadDelayTimerIntoRegister(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == LoadDelayTimerIntoRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return LoadDelayTimerIntoRegister(args[0], asm=asm)


class WaitForKeyPressLoadIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x0A

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return WaitForKeyPressLoadIntoRegister(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == WaitForKeyPressLoadIntoRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return WaitForKeyPressLoadIntoRegister(args[0], asm=asm)


class SetDelayTimerMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x15

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetDelayTimer(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SetDelayTimer.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SetDelayTimer(args[0], asm=asm)


class SetSoundTimerMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x18

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetSoundTimer(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SetSoundTimer.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SetSoundTimer(args[0], asm=asm)


class AddRegisterToAddressRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x1E

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return AddRegisterToAddressRegister(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == AddRegisterToAddressRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return AddRegisterToAddressRegister(args[0], asm=asm)


class SetAddressRegisterToSpriteInRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x29

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetAddressRegisterToSpriteInRegister(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == SetAddressRegisterToSpriteInRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return SetAddressRegisterToSpriteInRegister(args[0], asm=asm)


class BCDDecodeRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x33

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return BCDDecodeRegister(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == BCDDecodeRegister.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return BCDDecodeRegister(args[0], asm=asm)


class StoreRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x55

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return StoreRegisters(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == StoreRegisters.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return StoreRegisters(args[0], asm=asm)


class ReadRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x65

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return ReadRegisters(reg, op_code=op_code)

    def matches_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ins == ReadRegisters.MNEMONIC and len(args) == 1 and type(args[0]) == Register

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return ReadRegisters(args[0], asm=asm)


class FallBackMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return True

    def from_op_code(self, op_code):
        return Instruction([Raw(op_code)], op_code=op_code, asm="ERR!")

    def matches_asm(self, asm):
        return True

    def from_asm(self, asm):
        ins, args = AsmParser.parse_asm(asm)
        return Instruction(args, op_code=None, asm="ERR!")


class NotYetImplemented(Exception):  # customer exception type so I can pass in kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs

    def __repr__(self):
        return super().__repr__() + str(self.kwargs)


class UnknownAsmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs

    def __repr__(self):
        return super().__repr__() + str(self.kwargs)


MATCHERS = [  # this may be replaceable with InstructionMatcher.__subclasses__(), but I'm going to do it the dumb way for now
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
    LoadRegisterIntoRegisterMatcher(),
    OrRegistersMatcher(),
    AndRegistersMatcher(),
    XorRegistersMatcher(),
    AddRegistersMatcher(),
    SubtractRegistersMatcher(),
    ShiftRightRegisterMatcher(),
    ReverseSubtractRegistersMatcher(),
    ShiftLeftRegisterMatcher(),
    SkipNextInstructionIfRegistersNotEqualsMatcher(),
    SetAddressRegisterMatcher(),
    JumpToAddressPlusV0Matcher(),
    GenerateRandomNumberWithMaskMatcher(),
    DrawSpriteMatcher(),
    SkipIfKeyPressedMatcher(),
    SkipIfKeyNotPressedMatcher(),
    LoadDelayTimerIntoRegisterMatcher(),
    WaitForKeyPressLoadIntoRegisterMatcher(),
    SetDelayTimerMatcher(),
    SetSoundTimerMatcher(),
    AddRegisterToAddressRegisterMatcher(),
    SetAddressRegisterToSpriteInRegisterMatcher(),
    BCDDecodeRegisterMatcher(),
    StoreRegistersMatcher(),
    ReadRegistersMatcher(),
    FallBackMatcher(),
]

# returns an instruction object generated from the asm instruction
def parse_asm(asm):
    # ignore everything after the ';' (; is used to denote comments)
    asm = asm.split(";")[0]

    for matcher in MATCHERS:
        if matcher.matches_asm(asm):
            return matcher.from_asm(asm)
    return None


# returns the instruction object generated from the op_code
def parse_op_code(op_code):
    for matcher in MATCHERS:
        if matcher.matches_op_code(op_code):
            return matcher.from_op_code(op_code)
    return None
