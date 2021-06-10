#!/usr/bin/env python3

""" 
This file has all the test cases for the assembler/disassembler/Instruction-class DSL
There's better ways to implement this in python, but the purpose of this project was to learn about assemblers/disassemblers/emulators

"""
from lib import *

cases = [
    (0x0222, "SYS	a0x222", CallNativeCode(Address(0x222))),
    (0x00E0, "CLS", ClearScreen()),
    (0x00EE, "RTN", ReturnFromFunction()),
    (0x1234, "JMP	a0x234", JumpToAddress(Address(0x234))),
    (0x2345, "CALL	a0x345", CallFunction(Address(0x345))),
    (0x3144, "SE	v0x1 c0x44", SkipNextInstructionIfEqualsConst(Register(0x1), Constant(0x44))),
    (0x4233, "SNE	v0x2 c0x33", SkipNextInstructionIfNotEqualsConst(Register(0x2), Constant(0x33))),
    (0x50F0, "SRE	v0x0 v0xf", SkipNextInstructionIfRegistersEqual(Register(0x0), Register(0xF))),
    (0x6355, "LD	v0x3 c0x55", LoadConstantIntoRegister(Register(0x3), Constant(0x55))),
    (0x7422, "ADD	v0x4 c0x22", AddConstantToRegister(Register(0x4), Constant(0x22))),
    (0x8210, "LDR	v0x2 v0x1", LoadRegisterIntoRegister(Register(0x2), Register(0x1))),
    (0x8321, "OR	v0x3 v0x2", OrRegisters(Register(0x3), Register(0x2))),
    (0x8432, "AND	v0x4 v0x3", AndRegisters(Register(0x4), Register(0x3))),
    (0x8543, "XOR	v0x5 v0x4", XorRegisters(Register(0x5), Register(0x4))),
    (0x8654, "ADD	v0x6 v0x5", AddRegisters(Register(0x6), Register(0x5))),
    (0x8AB5, "SUB	v0xa v0xb", SubtractRegisters(Register(0xA), Register(0xB))),
    (0x8B06, "SHR	v0xb v0x0", ShiftRightRegister(Register(0xB), Register(0x0))),
    (0x8CB7, "SUBN	v0xc v0xb", ReverseSubtractRegisters(Register(0xC), Register(0xB))),
    (0x8FEE, "SHL	v0xf v0xe", ShiftLeftRegister(Register(0xF), Register(0xE))),
    (0x90F0, "SRNE	v0x0 v0xf", SkipNextInstructionIfRegistersNotEquals(Register(0x0), Register(0xF))),
    (0xA321, "LDI	a0x321", SetAddressRegister(Address(0x321))),
    (0xB111, "JMPR	a0x111", JumpToAddressPlusV0(Address(0x111))),
    (0xCDFF, "RNG	v0xd c0xff", GenerateRandomNumberWithMask(Register(0xD), Constant(0xFF))),
    (0xD121, "DRAW	v0x1 v0x2 n0x1", DrawSprite(Register(0x1), Register(0x2), Nibble(0x1))),
    (0xE29E, "SKP	v0x2", SkipIfKeyPressed(Register(0x2))),
    (0xE3A1, "SKNP	v0x3", SkipIfKeyNotPressed(Register(0x3))),
    (0xF107, "LDD	v0x1", LoadDelayTimerIntoRegister(Register(0x1))),
    (0xF90A, "WKPL	v0x9", WaitForKeyPressLoadIntoRegister(Register(0x9))),
    (0xF815, "SDT	v0x8", SetDelayTimer(Register(0x8))),
    (0xF718, "SST	v0x7", SetSoundTimer(Register(0x7))),
    (0xFB1E, "ADDI	v0xb", AddRegisterToAddressRegister(Register(0xB))),
    (0xFD29, "SISR	v0xd", SetAddressRegisterToSpriteInRegister(Register(0xD))),
    (0xFF33, "BCD	v0xf", BCDDecodeRegister(Register(0xF))),
    (0xFE55, "STR	v0xe", StoreRegisters(Register(0xE))),
    (0xFC65, "LDIR	v0xc", ReadRegisters(Register(0xC))),
]

if __name__ == "__main__":
    for op_code, asm, instruction in cases:
        assert instruction.op_code == op_code and instruction.asm == asm, ": {}\t{}|\t{}\t{}".format(
            instruction.op_code, op_code, instruction.asm, asm
        )
        parsed_op_code = parse_op_code(int.to_bytes(op_code, length=2, byteorder="big"))
        parsed_asm = parse_asm(asm)
        assert parsed_op_code == parsed_asm == instruction, "instruction object not equal: {}\t{}\t{}".format(
            parsed_op_code, parsed_asm, instruction
        )
        assert (
            int.from_bytes(parsed_op_code._op_code, byteorder="big") == parsed_op_code.op_code == op_code
        ), "op codes not equal: {}\t{}\t{}\t".format(
            "%#x" % int.from_bytes(parsed_op_code._op_code, byteorder="big"),
            "%#x" % parsed_op_code.op_code,
            "%#x" % op_code,
        )
        assert parsed_asm._asm == parsed_asm.asm == asm, "asm not equal: {}\t{}\t{}\t".format(
            parsed_asm._asm, parsed_asm.asm, asm
        )
        print("passed:\t{}\t{}\t\t\t{}".format(hex(op_code), asm, instruction))

    # special case for RAW
    op_code, asm, instruction = (
        0xFFFF,
        "ERR!	r0xFFFF ; comments are also supported",
        Instruction([], 0xFFFF, "ERR!	r0xffff"),
    )
    assert instruction.op_code == op_code, ": {}\t{}|\t{}\t{}".format(
        instruction.op_code, op_code, instruction.asm, asm
    )
    parsed_op_code = parse_op_code(int.to_bytes(op_code, length=2, byteorder="big"))
    # assert parsed_op_code == instruction, "instruction object not equal: {}\t{}".format(parsed_op_code, instruction)
    assert (
        int.from_bytes(parsed_op_code._op_code, byteorder="big") == parsed_op_code.op_code == op_code
    ), "op codes not equal: {}\t{}\t{}\t".format(
        "%#x" % int.from_bytes(parsed_op_code._op_code, byteorder="big"),
        "%#x" % parsed_op_code.op_code,
        "%#x" % op_code,
    )
    print("passed:\t{}\t{}\t\t\t{}".format(hex(op_code), asm, instruction))

    print("All test cases passed")
