#include <assert.h>
#include <stdlib.h>

#include "../src/chip8.h"
#include "../src/defs.h"

void testReturn() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x20fc};
  loadInstructions(toTest, ocs, 1);
  toTest->memory[0x0fc] = 0x00;
  toTest->memory[0x0fd] = 0xee;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x0fc);
  assert(toTest->stackPointer == 1);
  assert(toTest->stack[0] == 0x200);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->stackPointer == 0);
  free(toTest);
}

void testJump() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x10fc};
  loadInstructions(toTest, ocs, 1);
  emulateCycle(toTest);
  assert(toTest->programCounter == 0x00fc);
  free(toTest);
}

void testSubroutine() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x20fc};
  loadInstructions(toTest, ocs, 1);
  emulateCycle(toTest);
  assert(toTest->programCounter == 0x00fc);
  assert(toTest->stackPointer == 1);
  assert(toTest->stack[0] == 0x200);
  free(toTest);
}

void testSkipIfEqual() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x34fc, 0xFFFF, 0x34ff};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[4] = 0xfc;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204); // assert for skip

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206); // assert for not skipped
  free(toTest);
}

void testSkipIfNotEqual() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x40fc, 0x40ff, 0xFFFF};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0] = 0xfc;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202); // assert for not skip

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206); // assert for skipped
  free(toTest);
}

void testSkipIfRegEqual() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x5010, 0xffff, 0x5230};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0] = 0xfc;
  toTest->reg[1] = 0xfc;
  toTest->reg[2] = 0x00;
  toTest->reg[3] = 0xff;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204); // assert equal - skip

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206); // assert for not equal - dont skip
  free(toTest);
}

void testSetRegister() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x61fc};
  loadInstructions(toTest, ocs, 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[1] == 0xfc);
}

void testAddRegister() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x6622, 0x7622};
  loadInstructions(toTest, ocs, 2);

  emulateCycle(toTest); // Verify set is still working
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[6] == 0x22);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[6] == 0x44);
}

int main() {
  testReturn();
  testJump();
  testSubroutine();
  testSkipIfEqual();
  testSkipIfNotEqual();
  testSkipIfRegEqual();
  testSetRegister();
  testAddRegister();
}
