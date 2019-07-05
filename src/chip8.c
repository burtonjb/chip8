#include <stdio.h>
#include <stdlib.h>

#include "chip8.h"
#include "defs.h"

Chip8 *initChip8() {
  Chip8 *out = malloc(sizeof(Chip8));
  out->programCounter = PROGRAM_START;
  out->indexCounter = 0;
  out->stackPointer = 0;
  return out;
}

void loadInstructions(Chip8 *chip8, opcode *opcodes, int size) {
  for (int i = 0; i < size; i++) {
    chip8->memory[chip8->programCounter + 2 * i + 0] = opcodes[i] >> 8;
    chip8->memory[chip8->programCounter + 2 * i + 1] = opcodes[i] & 0xFF;
  }
}

void emulateCycle(Chip8 *chip8) {

  // fetch opcode. The opcode is 2 bytes, so need to do some shifting and or
  // magic
  opcode oc = chip8->memory[chip8->programCounter] << 8 |
              chip8->memory[chip8->programCounter + 1];

  // decode opcode (switch)
  switch (oc & 0xF000) {
  case 0x0000:
    if (oc == 0x0EE) { // return from subroutine
      if (chip8->stackPointer == 0) {
        printf("returned while stack is empty");
        exit(1);
      }
      chip8->programCounter = chip8->stack[--chip8->stackPointer];
      chip8->programCounter += 2;
    }
    if (oc == 0x0E0) { // TODO: Clear the display
    } else {           // Call RCA 1802 at NNN. Not needed for most ROMs
    }
    break;
  case 0x1000: // (0x1NNN) goto location NNN
    chip8->programCounter = oc & 0x0FFF;
    break;
  case 0x2000: // (0x2NNN) call subroutine at NNN
    if (chip8->stackPointer > STACK_SIZE) {
      printf("ran out of stack");
      exit(1);
    }
    chip8->stack[chip8->stackPointer++] = chip8->programCounter;
    chip8->programCounter = oc & 0x0FFF;
    break;
  case 0x3000: // (0x3XNN) Skip next instruction if VX == NN
    if (chip8->reg[(oc & 0x0F00) >> 8] == (oc & 0x00FF)) {
      chip8->programCounter += 2;
    }
    chip8->programCounter += 2;
    break;
  case 0x4000: // (0x4XNN) Skip next instruction if VX != NN
    if (chip8->reg[(oc & 0x0F00) >> 8] != (oc & 0x00FF)) {
      chip8->programCounter += 2;
    }
    chip8->programCounter += 2;
    break;
  case 0x5000: // (0x5XY0) Skip next instruction if VX == VY
    if (chip8->reg[(oc & 0x0F00) >> 8] == chip8->reg[(oc & 0x00F0) >> 4]) {
      chip8->programCounter += 2;
    }
    chip8->programCounter += 2;
    break;
  case 0x6000: // (0x6XNN) Sets VX to NN
    chip8->reg[(oc & 0x0F00) >> 8] = oc & 0x0FF;
    chip8->programCounter += 2;
    break;
  case 0x7000: // (0x7XNN) Adds NN to VX, not setting the carry flag
    chip8->reg[(oc & 0x0F00) >> 8] += oc & 0x0FF;
    chip8->programCounter += 2;
    break;
  default: // unknown op code
    print(chip8, false, false, false);
    printf("Unknown opcode %x \n", oc);
    exit(1); // Exit on failure
  }

  // TODO: update timers
}

void print(Chip8 *chip8, bool printMem, bool printReg, bool printStack) {
  printf("ProgramCounter: %x\n", chip8->programCounter);
  printf("IndexCounter: %x\n", chip8->indexCounter);
  printf("Current opcode: %x\n", chip8->memory[chip8->programCounter] << 8 |
                                     chip8->memory[chip8->programCounter + 1]);
  printf("Stackpointer: %d\n", chip8->stackPointer);

  if (printMem) {
    for (int i = 0; i < PROGRAM_END; i++) {
      printf("%x ", chip8->memory[i]);
      if (i % 80 == 0) {
        printf("\n");
      }
    }
    printf("\n");
  }

  if (printReg) {
    for (int i = 0; i < REGISTERS; i++) {
      printf("%x ", chip8->reg[i]);
    }
    printf("\n");
  }

  if (printStack) {
    for (int i = 0; i < STACK_SIZE; i++) {
      printf("%x ", chip8->stack[i]);
    }
    printf("\n");
  }
  printf("\n");
}
