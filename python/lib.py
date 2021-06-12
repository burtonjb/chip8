from instruction_matchers import *

# returns an instruction object generated from the asm instruction
def parse_asm(asm):
    # ignore everything after the ';' (; is used to denote comments)
    asm = asm.split(";")[0]

    for matcher in MATCHERS:
        if matcher.matches_asm(asm):
            return matcher.from_asm(asm)
    return None


# returns the instruction object generated from the op_code
def parse_op_code(op_code):
    for matcher in MATCHERS:
        if matcher.matches_op_code(op_code):
            return matcher.from_op_code(op_code)
    return None
