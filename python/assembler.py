#!/usr/bin/env python3

# usage: python3 disassembler.py ./PATH/TO/ROM

from lib import *
import argparse

parser = argparse.ArgumentParser(description="disassemble chip8 binaries into asm")
parser.add_argument("--file", type=str, help="[required] file path", required=True)
parser.add_argument("-old_asm", help="output the original asm", action="store_true")
parser.add_argument("-new_asm", help="output the asm after parsing", action="store_true")
parser.add_argument("-op", help="output the op codes after parsing", action="store_true")
parser.add_argument("--output", type=str, help="filepath for the output parsed binary")

args = parser.parse_args()

# formats the output for printing
def format_output(instruction):
    if instruction is None:
        return None
    out = ""
    if args.old_asm:
        out += str(instruction._asm) + "\t"
    if args.new_asm:
        out += str(instruction.asm) + "\t"
    if args.op:
        out += hex(instruction.op_code) + "\t"
    return out.strip()


def main():
    out = None
    if args.output:
        out = open(args.output, "wb")
    with open(args.file, "r") as f:
        line = "placeholder"
        while line:
            line = f.readline()
            if len(line) > 0:  # skip empty or short lines
                line = line.strip()
                instruction = parse_asm(line)
                print(format_output(instruction))
                if out:
                    out.write(instruction.op_code.to_bytes(2, byteorder="big"))
        if out:
            # out.write(b"\x00")
            out.close()


if __name__ == "__main__":
    main()
