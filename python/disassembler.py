#!/usr/bin/env python3

# usage: python3 disassembler.py --file ./PATH/TO/ROM -asm

from lib import *
import argparse

parser = argparse.ArgumentParser(description="disassemble chip8 binaries into asm")
parser.add_argument("--file", type=str, help="[required] file path", required=True)
parser.add_argument("-old_op", help="output the original op code", action="store_true")
parser.add_argument("-new_op", help="output the op code after parsing", action="store_true")
parser.add_argument("-asm", help="output the parsed asm instruction", action="store_true")
parser.add_argument(
    "-validate_op", help="checks that the outputted op codes are the same as the input", action="store_true"
)

args = parser.parse_args()

# formats the output for printing
def format_output(instruction):
    if instruction is None:
        return None
    out = ""
    if args.old_op:
        out += str(hex(instruction.op_code)) + "\t"
    if args.new_op:
        out += str(instruction._op_code.hex()) + "\t"
    if args.asm:
        out += str(instruction.asm) + "\t"
    return out.strip()


def main():
    with open(args.file, "rb") as f:
        op_code = None
        while op_code != b"":
            op_code = f.read(2)
            if len(op_code) == 2:
                instruction = parse_op_code(op_code)
                print(format_output(instruction))
                if args.validate_op:
                    assert (
                        int.from_bytes(op_code, byteorder="big") == instruction.op_code
                    ), "parsed op code is not the same: {}\t{}".format(
                        int.from_bytes(op_code, byteorder="big"), instruction.op_code
                    )


if __name__ == "__main__":
    main()
