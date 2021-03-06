#I have not added header tracking,                                             \
    so just clean and remake when a header file changes

EXE = chip8

SRC_DIR = src
TST_DIR = tst
OBJ_DIR = bin/obj
OUTPUT_DIR = bin

SRC = $(wildcard $(SRC_DIR)/*.c)
OBJ = $(SRC:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)
HEADERS = $(wildcard $(SRC_DIR)/*.h)

CPPFLAGS += -Iinclude
CFLAGS += -Wall -std=c11
LDFLAGS += -Llib
LDLIBS += -lm

.PHONY: all clean format fresh

all: $(EXE)

$(EXE): $(OBJ)
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $(OUTPUT_DIR)/$@ -Iinclude -lpthread -Llib -lSDL2 -lSDL2main

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	$(RM) $(OBJ)
	$(RM) $(OUTPUT_DIR)/$(EXE)

format:
	clang-format -i $(SRC_DIR)/*.c $(SRC_DIR)/*.h
	clang-format -i $(TST_DIR)/*.c
	black python/*.py --line-length 120

fresh: clean format all test

# TODO: clean up this target eventually
test:
	 gcc -std=c11 tst/test_chip8.c src/chip8.c -o bin/tst/chip8 && ./bin/tst/chip8
	 python3 python/test.py
