class Argument:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str(self.value)


## TODO: add validation to the arguments
class Address(Argument):  # 3 nibble value (12 bits)
    def __init__(self, value):
        super().__init__("Address", value)

    def __repr__(self):
        return hex(self.value)


class Constant(Argument):  # 2 nibble value (1 byte or 8 bits)
    def __init__(self, value):
        super().__init__("Constant", value)

    def __repr__(self):
        return hex(self.value)


class Nibble(Argument):  # 1 nibble value (4 bits, half a byte)
    def __init__(self, value):
        super().__init__("Nibble", value)


class Register(Argument):
    def __init__(self, value):
        super().__init__("Register", value)

    def __repr__(self):
        return "V{}".format(hex(self.value))


class Instruction:
    def __init__(self, op_code, mnenomic, args):
        self.op_code = op_code
        self.mnenomic = mnenomic  # these are mostly populated from cowgod's reverse engineered spec, but they may be slightly different
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


class LoadRegisterIntoRegister(Instruction):
    def __init__(self, op_code, reg_from, reg_to):
        super().__init__(op_code, "LDR", [reg_from, reg_to])


class OrRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "OR", [reg1, reg2])


class AndRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "AND", [reg1, reg2])


class XorRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "XOR", [reg1, reg2])


class AddRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "ADD", [reg1, reg2])


class SubtractRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "SUB", [reg1, reg2])


class ShiftRightRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SHR", [reg])


class ReverseSubtractRegisters(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "SUBN", [reg1, reg2])


class ShiftLeftRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SHL", [reg])


class SkipNextInstructionIfRegistersNotEquals(Instruction):
    def __init__(self, op_code, reg1, reg2):
        super().__init__(op_code, "SRNE", [reg1, reg2])


class SetAddressRegister(Instruction):
    def __init__(self, op_code, address):
        super().__init__(op_code, "LDI", [address])


class JumpToAddressPlusV0(Instruction):
    def __init__(self, op_code, address):
        super().__init__(op_code, "JPR", [address])


class GenerateRandomNumberWithMask(Instruction):
    def __init__(self, op_code, register, mask):
        super().__init__(op_code, "RNG", [register, mask])


class DrawSprite(Instruction):
    def __init__(self, op_code, reg1, reg2, nibble):
        super().__init__(op_code, "DRAW", [reg1, reg2, nibble])


class SkipIfKeyPressed(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SKP", [reg])


class SkipIfKeyNotPressed(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SKNP", [reg])


class LoadDelayTimerIntoRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "LDD", [reg])


class WaitForKeyPressLoadIntoRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "WKPL", [reg])


class SetDelayTimer(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SDT", [reg])


class SetSoundTimer(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SST", [reg])


class AddRegisterToAddressRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "ADDI", [reg])


class SetAddressRegisterToSpriteInRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "SISR", [reg])


class BCDDecodeRegister(Instruction):
    def __init__(self, op_code, reg):
        super().__init__(op_code, "BCD", [reg])


class StoreRegisters(Instruction):
    def __init__(self, op_code, last_register):
        super().__init__(op_code, "STR", [last_register])


class ReadRegisters(Instruction):
    def __init__(self, op_code, last_register):
        super().__init__(op_code, "LDIR", [last_register])


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


class LoadRegisterIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x00

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return LoadRegisterIntoRegister(op_code, reg1, reg2)


class OrRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x01

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return OrRegisters(op_code, reg1, reg2)


class AndRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x02

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return AndRegisters(op_code, reg1, reg2)


class XorRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x03

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return XorRegisters(op_code, reg1, reg2)


class AddRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x04

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return AddRegisters(op_code, reg1, reg2)


class SubtractRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x05

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return SubtractRegisters(op_code, reg1, reg2)


class ShiftRightRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0xFF) == 0x06

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return ShiftRightRegister(op_code, reg)


class ReverseSubtractRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0x0F) == 0x07

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return ReverseSubtractRegisters(op_code, reg1, reg2)


class ShiftLeftRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x80 and (op_code[1] & 0xFF) == 0xEE

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return ShiftLeftRegister(op_code, reg)


class SkipNextInstructionIfRegistersNotEqualsMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0x90
        # the spec actually expects this op code to end with a 0 -> e.g. 0x5XY0, but I'm going to allow any kind of value in the last nibble (which might be out of spec)
        # at least I'm being consistently overly permissive

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        return SkipNextInstructionIfRegistersNotEquals(op_code, reg1, reg2)


class SetAddressRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xA0

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return SetAddressRegister(op_code, address)


class JumpToAddressPlusV0Matcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xB0

    def from_op_code(self, op_code):
        address = Address(int.from_bytes(op_code, "big") & 0x0FFF)
        return JumpToAddressPlusV0(op_code, address)


class GenerateRandomNumberWithMaskMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xC0

    def from_op_code(self, op_code):
        register = Register(op_code[0] & 0x0F)
        const = Constant(op_code[1] & 0xFF)
        return GenerateRandomNumberWithMask(op_code, register, const)


class DrawSpriteMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xD0

    def from_op_code(self, op_code):
        reg1 = Register(op_code[0] & 0x0F)
        reg2 = Register(op_code[1] & 0xF0)
        nibble = Nibble(op_code[1] & 0x0F)
        return DrawSprite(op_code, reg1, reg2, nibble)


class SkipIfKeyPressedMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xE0 and (op_code[1] & 0xFF) == 0x9E

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SkipIfKeyPressed(op_code, reg)


class SkipIfKeyNotPressedMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xE0 and (op_code[1] & 0xFF) == 0xA1

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SkipIfKeyNotPressed(op_code, reg)


class LoadDelayTimerIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x07

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return LoadDelayTimerIntoRegister(op_code, reg)


class WaitForKeyPressLoadIntoRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x0A

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return WaitForKeyPressLoadIntoRegister(op_code, reg)


class SetDelayTimerMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x15

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetDelayTimer(op_code, reg)


class SetSoundTimerMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x18

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetSoundTimer(op_code, reg)


class AddRegisterToAddressRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x1E

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return AddRegisterToAddressRegister(op_code, reg)


class SetAddressRegisterToSpriteInRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x29

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return SetAddressRegisterToSpriteInRegister(op_code, reg)


class BCDDecodeRegisterMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x33

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return BCDDecodeRegister(op_code, reg)


class StoreRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x55

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return StoreRegisters(op_code, reg)


class ReadRegistersMatcher(InstructionMatcher):
    def matches_op_code(self, op_code):
        return (op_code[0] & 0xF0) == 0xF0 and (op_code[1] & 0xFF) == 0x65

    def from_op_code(self, op_code):
        reg = Register(op_code[0] & 0x0F)
        return ReadRegisters(op_code, reg)


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
]
