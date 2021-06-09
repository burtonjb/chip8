# usage: python3 disassembler.py ./PATH/TO/ROM

import sys

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
def format_output(op_code):
    return "{}".format(op_code.to_bytes(2, byteorder="big").hex())


# returns the op-code for the assembly instruction and args
def encode_op_code(instruction, args):
    if instruction == CALL_MACHINE_CODE:
        return 0x0000 ^ args[0]
    elif instruction == CLEAR_SCREEN:
        return 0x00E0
    elif instruction == RETURN_FROM_FUNCTION:
        return 0x00EE
    elif instruction == JUMP_TO_ADDRESS:
        return 0x1000 ^ args[0]
    elif instruction == CALL_FUNCTION:
        return 0x2000 ^ args[0]
    elif instruction == SKIP_NEXT_IF_EQUALS:
        return 0x3000 ^ (args[0] << 12) ^ (args[1])
    elif instruction == SKIP_NEXT_IF_NOT_EQUALS:
        return 0x4000 ^ (args[0] << 12) ^ (args[1])
    elif instruction == SKIP_IF_REG_X_EQ_REG_Y:
        return 0x5000 ^ (args[0] << 12) ^ (args[1] << 8)
    return 0xFFFF


def main():
    with open(sys.argv[1], "rw") as f:
        line = "placeholder"
        while line:
            line = f.readline().split("\t")
            mnenomic, args = line[0], line[1:]
            print(format_output(op_code, mnenomic, args))
            # handle end-of-file, output total size or something


def test_encoding():
    instructions = [
        ("CMC", [0x222]),
        ("CLS", []),
        ("RTN", []),
        ("JMP", [0x123]),
        ("CSR", [0x234]),
        ("BEQ", [0xA, 0xFF]),
        ("BNE", [0xB, 0xFE]),
        ("BRE", [0x1, 0x2]),
    ]
    for inst, args in instructions:
        print(format_output(encode_op_code(inst, args)))


if __name__ == "__main__":
    test_encoding()
    # main()
