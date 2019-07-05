#ifndef DEF_H
#define DEF_H

#define bool char
#define true 1
#define false 0

#define MAX_MEMORY 4096
#define REGISTERS 16
#define STACK_SIZE 16

#define MEM_START 0x00
#define INTERPRETER_END 0x1FF
#define GRAPHICS_START 0x050
#define GRAPHICS_END 0x0A0
#define PROGRAM_START 0x200
#define PROGRAM_END 0xFFF

typedef unsigned short opcode;
typedef unsigned short counter;
typedef unsigned short stack;
typedef unsigned char memory;

#endif // DEF_H
