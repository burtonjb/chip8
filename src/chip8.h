#ifndef CHIP_8_H
#define CHIP_8_H

#include "defs.h"

typedef struct {
  counter programCounter;
  counter indexCounter;
  stack stackPointer;

  memory memory[MAX_MEMORY];
  memory reg[REGISTERS];
  stack stack[STACK_SIZE];
} Chip8;

Chip8 *initChip8(); // Constructor

void loadInstructions(Chip8 *chip8, opcode *opcodes, int size);

void emulateCycle(Chip8 *chip8);

void print(Chip8 *chip8, bool printMem, bool printReg, bool printStack);

#endif // CHIP_8_H
