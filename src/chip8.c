#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "chip8.h"
#include "defs.h"

unsigned char chip8_fontset[FONT_SIZE] = {
    0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
    0x20, 0x60, 0x20, 0x20, 0x70, // 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
    0x90, 0x90, 0xF0, 0x10, 0x10, // 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
    0xF0, 0x10, 0x20, 0x40, 0x40, // 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, // A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
    0xF0, 0x80, 0x80, 0x80, 0xF0, // C
    0xE0, 0x90, 0x90, 0x90, 0xE0, // D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
    0xF0, 0x80, 0xF0, 0x80, 0x80  // F
};

Chip8 *initChip8() {
  Chip8 *out = malloc(sizeof(Chip8));
  out->programCounter = PROGRAM_START;
  out->indexCounter = 0;
  out->stackPointer = 0;

  memset(out->memory, 0, sizeof(out->memory));
  memset(out->reg, 0, sizeof(out->reg));
  memset(out->stack, 0, sizeof(out->stack));
  memset(out->graphics, 0, sizeof(out->graphics));
  memset(out->key, 0, sizeof(out->key));

  out->delayTimer = 0;
  out->soundTimer = 0;

  out->drawFlag = false;

  for (int i = 0; i < FONT_SIZE; i++) {
    out->memory[i + FONT_OFFSET] =
        chip8_fontset[i]; // TODO: should the be an offset for the memory
                          // location the fonts are loaded into?
  }

  return out;
}

void loadInstructions(Chip8 *chip8, opcode *opcodes, int size) {
  for (int i = 0; i < size; i++) {
    chip8->memory[chip8->programCounter + 2 * i + 0] = opcodes[i] >> 8;
    chip8->memory[chip8->programCounter + 2 * i + 1] = opcodes[i] & 0xFF;
  }
}

void emulateCycle(Chip8 *chip8) {

  // fetch opcode. The opcode is 2 bytes, so need to shift and then or
  opcode oc = chip8->memory[chip8->programCounter] << 8 |
              chip8->memory[chip8->programCounter + 1];

  // decode opcode and process opcode
  switch (oc & 0xF000) {
  case 0x0000:
    if (oc == 0x00EE) { // (0x00EE) return from subroutine
      if (chip8->stackPointer == 0) {
        printf("returned while stack is empty");
        exit(1);
      }
      chip8->programCounter = chip8->stack[--chip8->stackPointer];
      chip8->programCounter += 2;
    }
    else if (oc == 0x00E0) { // (0x00E0) Clear the display
      for (int i = 0; i < GRAPHICS_WIDTH * GRAPHICS_HEIGHT; i++) {
        chip8->graphics[i] = 0;
      }
      chip8->drawFlag = true;
      chip8->programCounter += 2;
    } else { // (0x0NNN) Call RCA 1802 at NNN. Not needed for most ROMs, so just going to error out
      print(chip8, false, false, false);
      printf("Unknown opcode %.4x \n", oc);
      exit(1);
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
  case 0x8000:
    if ((oc & 0x000F) == 0) { //(0x8XY0) Set VX = VY
      chip8->reg[(oc & 0x0F00) >> 8] = chip8->reg[(oc & 0x00F0) >> 4];
    } else if ((oc & 0x000F) == 1) { //(0x8XY1) VX = VX|VY (or)
      chip8->reg[(oc & 0x0F00) >> 8] |= chip8->reg[(oc & 0x00F0) >> 4];
    } else if ((oc & 0x000F) == 2) { //(0x8XY2) VX = VX&VY (and)
      chip8->reg[(oc & 0x0F00) >> 8] &= chip8->reg[(oc & 0x00F0) >> 4];
    } else if ((oc & 0x000F) == 3) { //(0x8XY3) VX = VX^VY (xor)
      chip8->reg[(oc & 0x0F00) >> 8] ^= chip8->reg[(oc & 0x00F0) >> 4];
    } else if ((oc & 0x000F) ==
               4) { //(0x8XY4) VX = VX+VY. Also sets the carry flag
      memory sum =
          chip8->reg[(oc & 0x0F00) >> 8] + chip8->reg[(oc & 0x00F0) >> 4];
      chip8->reg[0xf] = (sum < chip8->reg[(oc & 0x0F00) >> 8]) ||
                        (sum < chip8->reg[(oc & 0x00F0) >> 4]);
      chip8->reg[(oc & 0x0F00) >> 8] = sum;
    } else if ((oc & 0x000F) ==
               5) { //(0x8XY6) VX = VX-VY. Also sets the borrow flag
      chip8->reg[0xf] =
          (chip8->reg[(oc & 0x00F0) >> 4] <= chip8->reg[(oc & 0x0F00) >> 8]);
      chip8->reg[(oc & 0x0F00) >> 8] -= chip8->reg[(oc & 0x00F0) >> 4];
    } else if ((oc & 0x000F) ==
               6) { //(0x8XY6) Stores the least sig. bit in VF. Then VX >> 1
      chip8->reg[0xF] = chip8->reg[(oc & 0x0F00) >> 8] & 0x0001;
      chip8->reg[(oc & 0x0F00) >> 8] >>= 1;
    } else if ((oc & 0x000F) ==
               7) { //(0x8XY7) Sets Vx = Vy - Vx. Sets the borrow
      chip8->reg[0xF] =
          (chip8->reg[(oc & 0x0F00) >> 8] <= chip8->reg[(oc & 0x00F0) >> 4]);
      chip8->reg[(oc & 0x0F00) >> 8] =
          chip8->reg[(oc & 0x00F0) >> 4] - chip8->reg[(oc & 0x0F00) >> 8];
    } else if ((oc & 0x000F) ==
               0xE) { // (0x8XYE) Stores the most sig. bit in VF. Then VX << 1
      chip8->reg[0xF] = chip8->reg[(oc & 0x0F00) >> 8] >> 7;
      chip8->reg[(oc & 0x0F00) >> 8] <<= 1;
    } else {
      print(chip8, false, false, false);
      printf("Unknown opcode %.4x \n", oc);
      exit(1);
    }
    chip8->programCounter += 2;
    break;
  case 0x9000: // (0x9XY0) Skip the next instruction if Vx != Vy
    if (chip8->reg[(oc & 0x0F00) >> 8] != chip8->reg[(oc & 0x00F0) >> 4]) {
      chip8->programCounter += 2;
    }
    chip8->programCounter += 2;
    break;
  case 0xA000: // (0xANNN) Set the indexCounter to NNN
    chip8->indexCounter = oc & 0x0FFF;
    chip8->programCounter += 2;
    break;
  case 0xB000: // (0xBNNN) Jump to instruction NNN + V0
    chip8->programCounter = (oc & 0x0FFF) + chip8->reg[0];
    break;
  case 0xC000: // (0xCXNN) Set VX to NN and some random number
    chip8->reg[(oc & 0x0F00) >> 8] = (rand() % (0xFF + 1)) & (oc & 0x00FF);
    chip8->programCounter += 2;
    break;
  case 0xD000:; // (0xDXYN) Draws a sprite at coordinate (VX, VY) that has a
                // width of 8 pixels and a height of N pixels. Each row of 8
                // pixels is read as bit-coded starting from memory location I;
                // I value doesn’t change after the execution of this
                // instruction. As described above, VF is set to 1 if any screen
                // pixels are flipped from set to unset when the sprite is
                // drawn, and to 0 if that doesn’t happen
    memory x = chip8->reg[(oc & 0x0F00) >> 8];
    memory y = chip8->reg[(oc & 0x00F0) >> 4];
    memory height = oc & 0x000F;
    chip8->reg[0xf] = 0;
    memory pixel;
    for (int yline = 0; yline < height; yline++) {
      pixel = chip8->memory[chip8->indexCounter + yline];
      for (int xline = 0; xline < 8; xline++) {
        if ((pixel & (0x80 >> xline)) != 0) {
          if (chip8->graphics[(x + xline + ((y + yline) * 64))] == 1) {
            chip8->reg[0xf] = 1;
          }
          chip8->graphics[x + xline + ((y + yline) * 64)] ^= 1;
        }
      }
    }
    chip8->drawFlag = true;
    chip8->programCounter += 2;
    break;
  case 0xE000:
    if ((oc & 0x00FF) == 0x009E) { // (0xEX9E) Skip if key(Vx) is pressed
      if (chip8->key[chip8->reg[(oc & 0x0F00) >> 8]] == true) {
        chip8->programCounter += 2;
      }
    } else if ((oc & 0x0FF) ==
               0x00A1) { // (0xEXA1) Skip if key(Vx) is not pressed
      if (chip8->key[chip8->reg[(oc & 0x0F00) >> 8]] == false) {
        chip8->programCounter += 2;
      }
    } else {
      print(chip8, false, false, false);
      printf("Unknown opcode %.4x \n", oc);
      exit(1);
    }
    chip8->programCounter += 2;
    break;
  case 0xF000:
    if ((oc & 0x00FF) == 0x0007) { // (0xFX07) Set Vx to delayTimer
      chip8->reg[(oc & 0x0F00) >> 8] = chip8->delayTimer;
    } else if ((oc & 0x00FF) ==
               0x000A) { // (0xFX0A) Wait for keypress. Store key in Vx
      bool keyPressed = false;
      for (int i = 0; i < KEYS; i++) {
        if (chip8->key[i] == true) {
          chip8->reg[(oc & 0x0F00) >> 8] = i;
        }
      }
      if (!keyPressed)
        return;
    } else if ((oc & 0x00FF) == 0x0015) { // (0xFX15) Set delay timer to Vx
      chip8->delayTimer = chip8->reg[(oc & 0x0F00) >> 8];
    } else if ((oc & 0x00FF) == 0x0018) { // (0x0FX18) Set sound timer to Vx
      chip8->soundTimer = chip8->reg[(oc & 0x0F00) >> 8];
    } else if ((oc & 0x00FF) == 0x001E) { // (0xFX1E) Adds Vx to I
      // Set Vf to 1 when there is a range overflow, otherwise set to 0
      chip8->reg[0xf] =
          (chip8->indexCounter + chip8->reg[(oc & 0x0F00) >> 8] > 0x0FFF);
      chip8->indexCounter += chip8->reg[(oc & 0x0F00) >> 8];
    } else if ((oc & 0x00FF) ==
               0x0029) { // (0xFX29) Sets I to the location of the sprite for
                         // the character in VX. Characters 0-F (in hexadecimal)
                         // are represented by a 4x5 font.
      chip8->indexCounter = chip8->reg[(oc & 0x0F00) >> 8] * 0x5;
    } else if ((oc & 0x00FF) ==
               0x0033) { // (0xFX33) Stores the binary-coded decimal
                         // representation of VX, with the most significant of
                         // three digits at the address in I, the middle digit
                         // at I plus 1, and the least significant digit at I
                         // plus 2. (In other words, take the decimal
                         // representation of VX, place the hundreds digit in
                         // memory at location in I, the tens digit at location
                         // I+1, and the ones digit at location I+2.)
      chip8->memory[chip8->indexCounter] = chip8->reg[(oc & 0x0F00) >> 8] / 100;
      chip8->memory[chip8->indexCounter + 1] =
          (chip8->reg[(oc & 0x0F00) >> 8] / 10) % 10;
      chip8->memory[chip8->indexCounter + 2] =
          chip8->reg[(oc & 0x0F00) >> 8] % 10;
    } else if ((oc & 0x00FF) ==
               0x0055) { // (0xFX55) Stores V0 to VX (including VX) in memory
                         // starting at address I. The offset from I is
                         // increased by 1 for each value written, but I itself
                         // is left unmodified.
      for (int i = 0; i <= ((oc & 0x0F00) >> 8); ++i) {
        chip8->memory[chip8->indexCounter + i] = chip8->reg[i];
      }
      chip8->indexCounter += ((oc & 0x0F00) >> 8) + 1;
    } else if ((oc & 0x00FF) ==
               0x0065) { // (0xFX65) Fills V0 to VX (including VX) with values
                         // from memory starting at address I. The offset from I
                         // is increased by 1 for each value written, but I
                         // itself is left unmodified.
      for (int i = 0; i <= ((oc & 0x0F00) >> 8); ++i) {
        chip8->reg[i] = chip8->memory[chip8->indexCounter + i];
      }
      chip8->indexCounter += ((oc & 0x0F00) >> 8) + 1;
    }
    chip8->programCounter += 2;
    break;
  default: // unknown op code
    print(chip8, false, false, false);
    printf("Unknown opcode %.4x \n", oc);
    exit(1);
  }

  // update timers
  if (chip8->delayTimer > 0) {
    --chip8->delayTimer;
  }
  if (chip8->soundTimer > 0) {
    if (chip8->soundTimer == 1) {
      printf("\a"); // Beep control character}
      --chip8->soundTimer;
    }
  }
}

void print(Chip8 *chip8, bool printMem, bool printReg, bool printStack) {
  printf("ProgramCounter: %.4X\n", chip8->programCounter);
  printf("IndexCounter: %.4X\n", chip8->indexCounter);
  printf("Current opcode: %.4X\n", chip8->memory[chip8->programCounter] << 8 |
                                     chip8->memory[chip8->programCounter + 1]);
  printf("Stackpointer: %.4X\n", chip8->stackPointer);

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
