from instructions import *


class InstructionMatcher:
    """
  Class that maps a binary/integer op code or string representation of asm to a "Instruction" object
  """

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
