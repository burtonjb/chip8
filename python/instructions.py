from arguments import *


class Instruction:
    """
    Represents a chip8 instruction/op code. These objects can output representations of themselves in binary/op-code or asm
  """

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
