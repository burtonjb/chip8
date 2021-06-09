# usage: python3 disassembler.py ./PATH/TO/ROM

import sys
from shared import *

UNDEFINED_OP_CODE = "ERR!"
CALL_MACHINE_CODE = "CMC"
CLEAR_SCREEN = "CLS"
RETURN_FROM_FUNCTION = "RTN"
JUMP_TO_ADDRESS = "JMP"
CALL_FUNCTION = "CSR"
SKIP_NEXT_IF_EQUALS = "BEQ"
SKIP_NEXT_IF_NOT_EQUALS = "BNE"
SKIP_IF_REG_X_EQ_REG_Y = "BRE"

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
            mnenomic, args = decode_op_code(op_code)
            print(format_output(op_code, mnenomic, args))
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
        0x7422,  # add 22 to v4
    ]
    for code in op_codes:
        code = code.to_bytes(2, byteorder="big")
        print(format_output(decode_op_code(code)))


if __name__ == "__main__":
    test_decoding()
    # main()
