#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "chip8.h"
#include "defs.h"

int main(int argc, char **argv) {
  Chip8 *chip8 = initChip8();
  srand(time(0));
  chip8->memory[chip8->programCounter] = 0xA2;
  chip8->memory[chip8->programCounter + 1] = 0xF0;
  opcode oc = chip8->memory[chip8->programCounter] << 8 |
              chip8->memory[chip8->programCounter + 1];
  printf("%x\n", oc);
  return 0;
}
