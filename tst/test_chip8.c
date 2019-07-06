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

void testClearScreen() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x00E0};
  toTest->graphics[7] = 1;

  loadInstructions(toTest, ocs, 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x0202);
  assert(toTest->graphics[7] == 0);
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

void testSetRegToReg() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x8ab0};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0xb] = 0xab;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0xa] == 0xab);
  assert(toTest->reg[0xb] == 0xab);
}

void testOrRegisters() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x8cd1};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0xc] = 0xf0;
  toTest->reg[0xd] = 0x0f;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0xc] == 0xff);
  assert(toTest->reg[0xd] == 0x0f);
}

void testAndRegisters() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x8792};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0x7] = 0xfa;
  toTest->reg[0x9] = 0xaf;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x7] == 0xaa);
  assert(toTest->reg[0x9] == 0xaf);
}

void testXorRegisters() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x81a3};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0x1] = 0x7a;
  toTest->reg[0xa] = 0x92;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x1] == 0xe8);
  assert(toTest->reg[0xa] == 0x92);
}

void testAddRegisters() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x8134, 0x8134, 0x8134};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0x1] = 0xfe;
  toTest->reg[0x3] = 0x01;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x1] == 0xff);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 0);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[0x1] == 0x00);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206);
  assert(toTest->reg[0x1] == 0x01);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 0);
}

void testSubtractRegisters() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x8135, 0x8135, 0x8135};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0x1] = 0x01;
  toTest->reg[0x3] = 0x01;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x1] == 0x00);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[0x1] == 0xff);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 0);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206);
  assert(toTest->reg[0x1] == 0xfe);
  assert(toTest->reg[0x3] == 0x01);
  assert(toTest->reg[0xf] == 1);
}

void testRightShift() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x8006, 0x8006, 0x8006};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0x0] = 0x05;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x0] == 0x02);
  assert(toTest->reg[0xf] == 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[0x0] == 0x01);
  assert(toTest->reg[0xf] == 0);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206);
  assert(toTest->reg[0x0] == 0x00);
  assert(toTest->reg[0xf] == 1);
}

void testReverseSubtract() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x8a57, 0x8a57};
  loadInstructions(toTest, ocs, 2);
  toTest->reg[0xa] = 0x01;
  toTest->reg[0x5] = 0x03;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0xa] == 0x02);
  assert(toTest->reg[0x5] == 0x03);
  assert(toTest->reg[0xf] == 1);

  toTest->reg[0xa] = 0x03;
  toTest->reg[0x5] = 0x01;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[0xa] == 0xfe);
  assert(toTest->reg[0x5] == 0x01);
  assert(toTest->reg[0xf] == 0x00);
}

void testLeftShift() {
  Chip8 *toTest = initChip8();
  opcode ocs[] = {0x850E, 0x850E, 0x850E};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0x5] = 0x2a;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->reg[0x5] == 0x54);
  assert(toTest->reg[0xf] == 0);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x204);
  assert(toTest->reg[0x5] == 0xa8);
  assert(toTest->reg[0xf] == 0);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206);
  assert(toTest->reg[0x5] == 0x50);
  assert(toTest->reg[0xf] == 1);
}

void testSkipIfRegNotEqual() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0x9010, 0x9230, 0xffff};
  loadInstructions(toTest, ocs, 3);
  toTest->reg[0] = 0xfc;
  toTest->reg[1] = 0xfc;
  toTest->reg[2] = 0x00;
  toTest->reg[3] = 0xff;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202); // assert equal - dont skip

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x206); // assert for not equal - skip
  free(toTest);
}

void testSetIndexCounter() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0xaec2};
  loadInstructions(toTest, ocs, 1);

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  assert(toTest->indexCounter == 0x0ec2);
}

void testJumpToAddressAndReg() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0xb001};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0] = 0x01;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x002);
}

void testRandMask() {
  Chip8 *toTest = initChip8();

  opcode ocs[] = {0xC0FF};
  loadInstructions(toTest, ocs, 1);
  toTest->reg[0] = 0x01;

  emulateCycle(toTest);
  assert(toTest->programCounter == 0x202);
  // Can't really test random value here;
}

int main(int argc, char **argv) {
  testReturn();
  testClearScreen();
  testJump();
  testSubroutine();
  testSkipIfEqual();
  testSkipIfNotEqual();
  testSkipIfRegEqual();
  testSetRegister();
  testAddRegister();
  testSetRegToReg();
  testOrRegisters();
  testAndRegisters();
  testXorRegisters();
  testAddRegisters();
  testSubtractRegisters();
  testRightShift();
  testReverseSubtract();
  testLeftShift();
  testSkipIfRegNotEqual();
  testSetIndexCounter();
  testJumpToAddressAndReg();
  testRandMask();
  // TODO: test cases for draw and later
}
