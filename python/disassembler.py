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
def format_output(op_code, nemonic, nemonic_args):
    return "{}\t{}\t{}".format(op_code.hex(), nemonic, nemonic_args)

# returns the nemonic for the op-code, plus any args
def decode_op_code(op_code):
    first_byte = op_code[0]
    second_byte = op_code[1]
    if (first_byte & 0xF0) == 0x00:
        if second_byte == 0xE0:
            return CLEAR_SCREEN, None
        elif second_byte == 0xEE:
            return RETURN_FROM_FUNCTION, None
        else:
            return (
                CALL_MACHINE_CODE,
                hex(int.from_bytes(op_code, byteorder="big") & 0x0FFF),
            )
    elif (first_byte & 0xF0) == 0x10:
        return JUMP_TO_ADDRESS, hex(int.from_bytes(op_code, byteorder="big") & 0x0FFF)
    elif (first_byte & 0xF0) == 0x20:
        return CALL_FUNCTION, hex(int.from_bytes(op_code, byteorder="big") & 0x0FFF)
    elif (first_byte & 0xF0) == 0x30:
        return SKIP_NEXT_IF_EQUALS, (hex(int.from_bytes(op_code, byteorder="big") & 0x0F), hex(int.from_bytes(op_code, byteorder="big") & 0x00FF))
    elif (first_byte & 0xF0) == 0x40:
        return SKIP_NEXT_IF_NOT_EQUALS, (hex(int.from_bytes(op_code, byteorder="big") & 0x0F), hex(int.from_bytes(op_code, byteorder="big") & 0x00FF))
    elif (first_byte & 0xF0) == 0x50:
        # technically this should end only with a 0, but I don't think its worth validating this
        return SKIP_IF_REG_X_EQ_REG_Y, (hex(int.from_bytes(op_code, byteorder="big") & 0x0F), hex(int.from_bytes(op_code, byteorder="big") & 0x00F0))
    return UNDEFINED_OP_CODE, None


def main():
    with open(sys.argv[1], "rb") as f:
        op_code = None
        while op_code != b"":
            op_code = f.read(2)
            nemonic, args = decode_op_code(op_code)
            print(format_output(op_code, nemonic, args))
            # handle end-of-file, output total size or something


def test_decoding():
    op_codes = [0x0222, 0x00E0, 0x00EE, 0x1234, 0x2345, 0x3144, 0x4233, 0x50F0]
    for code in op_codes:
        code = code.to_bytes(2, byteorder="big")
        print(format_output(code, *decode_op_code(code)))


if __name__ == "__main__":
    test_decoding()
    # main()
