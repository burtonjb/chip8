# overview of chip8
CHIP-8 is an interpreted programming language used in the mid-1970s. There are many classic video games ported to the chip-8 interpreter.

# memory model
The Chip-8 language is capable of accessing up to 4KB (4,096 bytes) of RAM, from location 0x000 (0) to 0xFFF (4095). The first 512 bytes, from 0x000 to 0x1FF, are where the original interpreter was located, and should not be used by programs.

Most Chip-8 programs start at location 0x200 (512), but some begin at 0x600 (1536).

Chip-8 has 16 general purpose 8-bit registers, usually referred to as Vx, where x is a hexadecimal digit (0 through F). There is also a 16-bit register called I. This register is generally used to store memory addresses, so only the lowest (rightmost) 12 bits are usually used.

The VF register should not be used by any program, as it is used as a flag by some instructions. 

The computers which originally used the Chip-8 Language had a 16-key hexadecimal keypad with the following layout:

<pre>
1	2	3	C
4	5	6	D
7	8	9	E
A	0	B	F
</pre>

This layout must be mapped into various other configurations to fit the keyboards of today's platforms.

The original implementation of the Chip-8 language used a 64x32-pixel monochrome display with this format:

<pre>
(0,0)	(63,0)
(0,31)	(63,31)
</pre>

Chip-8 provides 2 timers, a delay timer and a sound timer. Their frequency is both 60Hz

# opcodes

|Opcode|Description|
|---|---|
|0NNN	| Calls RCA 1802 program at address NNN. Not necessary for most ROMs.
|00E0	|	Clears the screen.
|00EE	|	Returns from a subroutine.
|1NNN	|	Jumps to address NNN.
|2NNN	|	Calls subroutine at NNN.
|3XNN	|	Skips the next instruction if VX equals NN. (Usually the next instruction is a jump to skip a code block)
|4XNN	|	Skips the next instruction if VX doesn't equal NN. (Usually the next instruction is a jump to skip a code block)
|5XY0	|	Skips the next instruction if VX equals VY. (Usually the next instruction is a jump to skip a code block)
|6XNN	|	Sets VX to NN.
|7XNN	|	Adds NN to VX. (Carry flag is not changed)
|8XY0	|	Sets VX to the value of VY.
|8XY1	|	Sets VX to VX or VY. (Bitwise OR operation)
|8XY2	|	Sets VX to VX and VY. (Bitwise AND operation)
|8XY3	|	Sets VX to VX xor VY.
|8XY4	|	Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't.
|8XY5	|	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
|8XY6	|	Stores the least significant bit of VX in VF and then shifts VX to the right by 1.[2]
|8XY7	|	Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
|8XYE	|	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[3]
|9XY0	|	Skips the next instruction if VX doesn't equal VY. (Usually the next instruction is a jump to skip a code block)
|ANNN	| Sets I to the address NNN.
|BNNN	|	Jumps to the address NNN plus V0.
|CXNN	|	Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
|DXYN	|	Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded starting from memory location I; I value doesn’t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn’t happen
|EX9E	|	Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block)
|EXA1	|	Skips the next instruction if the key stored in VX isn't pressed. (Usually the next instruction is a jump to skip a code block)
|FX07	|	Sets VX to the value of the delay timer.
|FX0A	|	A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)
|FX15	|	Sets the delay timer to VX.
|FX18	|	Sets the sound timer to VX.
|FX1E	|	Adds VX to I.[4]
|FX29	|	Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
|FX33	|Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)
|FX55	| Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.
|FX65| Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.

# Dependencies for this project
 * basic C development (sudo apt-get install build-essential)
 * clang-format (sudo apt-get install clang-format) [not required]
 * SDL2 (sudo apt-get install libsdl2-dev) [required for graphics]

# How to use
chip8 /PATH/TO/ROM

# 2021 update
I ended up adding a really simple disassembler and assembler to this project. I wrote them in python insead of C for two reasons:
1. Python is an OOP language and I wanted to do some OOP design
2. String manipulation in C is hard, its easy in python

They can be run by running, with more options available by passing in '-h' as an argument.

```
python3 python/disassembler.py --file ./roms/PUZZLE -new_op -old_op -asm
python3 python/assembler.py --file ./bin/asm/PUZZLE.asm -op -new_asm -old_asm
```

Additionally, instead of learning my poorly spec'd asm instruction set, you can also write code in 
the slightly too verbose python DSL like language I created. See the test cases for more details, but you can do something like:

```
f = open(SOME_FILE, 'wb')
instructions = [
    CallNativeCode(Address(0x222)),
    ClearScreen(),
    JumpToAddress(Address(0x200)),
]
for i in instructions:
  f.write(i.op_code)
f.close()
```

### For the design of the assembler/disassembler:
I used some kind of pattern-matching like technique, mapping them back to the instruction "sum type/class".
Not super complicated if you're familiar with this FP pattern, but required a couple tries to get all the APIs
working the way I wanted. 

# sources
* https://en.wikipedia.org/wiki/CHIP-8
* http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
* http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
