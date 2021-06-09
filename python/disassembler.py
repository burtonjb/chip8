#!/usr/bin/env python3

# usage: python3 disassembler.py ./PATH/TO/ROM

import sys
from shared import *

# formats the output for printing
def format_output(instruction):
    if instruction is None:
        return None
    return "{}\t{}\t{}".format(
        instruction.op_code.hex(), instruction.mnenomic, instruction.args
    )


# returns the mnenomic for the op-code, plus any args
def decode_op_code(op_code):
    for matcher in MATCHERS:
        if matcher.matches_op_code(op_code):
            return matcher.from_op_code(op_code)
    return None


def main():
    with open(sys.argv[1], "rb") as f:
        op_code = None
        while op_code != b"":
            op_code = f.read(2)
            instruction = decode_op_code(op_code)
            print(format_output(instruction))
        # handle end-of-file, output total size or something


def test_decoding():
    op_codes = [
        0x0222,  # sys call address 222
        0x00E0,  # clear screen
        0x00EE,  # return
        0x1234,  # jump to instruction 234
        0x2345,  # "call function" at instruction 345 (jump to 345 and push the calling address to the stack)
        0x3144,  # skip next instruction if v1 == 44
        0x4233,  # skip next instruction if v2 != 33
        0x50F0,  # skip next instruction if v0 == vf
        0x6355,  # load 55 into v3
        0x7422,  # add 22 to v4,
        0x8210,  # set v2 = v1
        0x8321,  # v3 = v3 | v2
        0x8432,  # v4 = v4 & v3
        0x8543,  # v5 = v5 XOR v4
        0x8654,  # v6 = v6 + v5
        0x8AB5,  # va = va - vb
        0x8B06,  # vb = vb >> 1 (right shift vb 1)
        0x8CB7,  # vc = vb - vc (reverse of sub)
        0x8FEE,  # vf << 1 (left shift vf 1)
        0x90F0,  # skip next instruction if v0 != vf
        0xA321,  # set I (the address register) to 321
        0xB111,  # Jump to address 111 + v0
        0xCDFF,  # set vD to (random masked with FF)
        0xD121,  # draw 1 byte sprite located at memory location starting at the index counter to location (v1, v2)
        0xE29E,  # skip the next value if the key[value of v2] is pressed
        0xE3A1,  # skip the next value if the key[value of v3] is not pressed
        0xF107,  # load the value of the delay timer into v1
        0xF90A,  # wait for a key to be pressed, store the index of the key pressed into v9.
        0xF815,  # set the delay timer to the value of v8
        0xF718,  # set the sound timer to the value of v7
        0xFB1E,  # I = I + vb
        0xFD29,  # I = location of sprite for digit vd.
        0xFF33,  # stores BCD representation of vf into I, I+1, I+2
        0xFE55,  # stores values of registers v0 through ve into memory, starting at I
        0xFC65,  # read registers v0 through vc from memory, starting at I
        0xFFFF,  # unknown instruction (not defined in the spec)
    ]
    for code in op_codes:
        code = code.to_bytes(2, byteorder="big")
        print(format_output(decode_op_code(code)))


if __name__ == "__main__":
    test_decoding()
    # main()
