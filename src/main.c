#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "chip8.h"
#include "defs.h"

#include "SDL2/SDL.h"

#define WINDOW_WIDTH 1024
#define WINDOW_HEIGHT 512

key keyMap[KEYS] = {SDLK_1, SDLK_2, SDLK_3, SDLK_4, SDLK_q, SDLK_w,
                    SDLK_e, SDLK_r, SDLK_a, SDLK_s, SDLK_d, SDLK_f,
                    SDLK_z, SDLK_x, SDLK_c, SDLK_v};

void loadRom(Chip8 *chip8, int argc, char **argv) {
  if (argc != 2) {
    printf("1st argument must be path to rom\n");
    exit(EXIT_FAILURE);
  }
  FILE *fp;
  fp = fopen(argv[1], "rb");
  if (fp == NULL) {
    printf("Failed to open rom: %s\n", argv[1]);
    exit(EXIT_FAILURE);
  }
  fseek(fp, 0, SEEK_END);
  long romSize = ftell(fp);
  rewind(fp);

  unsigned char *romBuffer =
      (unsigned char *)malloc(sizeof(unsigned char) * romSize);
  if (romBuffer == NULL) {
    printf("Failed to allocate memory for ROM\n");
    exit(EXIT_FAILURE);
  }
  unsigned int result =
      fread(romBuffer, sizeof(char), (unsigned int)romSize, fp);
  if (result != romSize) {
    printf("Failed to read ROM\n");
    exit(EXIT_FAILURE);
  }
  if (romSize < PROGRAM_END - PROGRAM_START) {
    for (int i = 0; i < romSize; ++i) {
      chip8->memory[i + PROGRAM_START] = (unsigned char)romBuffer[i];
    }
  } else {
    printf("ROM too large to fit in memory\n");
    exit(EXIT_FAILURE);
  }
  fclose(fp);
  free(romBuffer);
}

int main(int argc, char **argv) {
  Chip8 *chip8 = initChip8();

  srand(time(0)); // set rand seed

  loadRom(chip8, argc, argv);

  print(chip8, true, true, true);

  // Initialize SDL
  SDL_Init(SDL_INIT_VIDEO);
  SDL_Window *window =
      SDL_CreateWindow("CHIP-8 Emulator", SDL_WINDOWPOS_UNDEFINED,
                       SDL_WINDOWPOS_UNDEFINED, WINDOW_WIDTH, WINDOW_HEIGHT, 0);
  SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, 0);
  SDL_RenderSetLogicalSize(renderer, WINDOW_WIDTH, WINDOW_HEIGHT);
  SDL_Texture *sdlTexture = SDL_CreateTexture(
      renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, 64, 32);
  SDL_RenderClear(renderer);

  uint32_t pixels[GRAPHICS_WIDTH * GRAPHICS_HEIGHT];

  while (true) {
    emulateCycle(chip8);

    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) {
        exit(0);
      }
      // Process keydown events
      if (e.type == SDL_KEYDOWN) {
        if (e.key.keysym.sym == SDLK_ESCAPE) {
          exit(0);
        }

        for (int i = 0; i < KEYS; ++i) {
          if (e.key.keysym.sym == keyMap[i]) {
            chip8->key[i] = 1;
          }
        }
      }
      if (e.type == SDL_KEYUP) {
        for (int i = 0; i < 16; ++i) {
          if (e.key.keysym.sym == keyMap[i]) {
            chip8->key[i] = 0;
          }
        }
      }
    }

    if (chip8->drawFlag == true) {
      chip8->drawFlag = false;

      // Store pixels in temporary buffer
      for (int i = 0; i < GRAPHICS_WIDTH * GRAPHICS_HEIGHT; ++i) {
        memory pixel = chip8->graphics[i];
        pixels[i] = (0x00FFFFFF * pixel) | 0xFF000000;
      }

      // Update SDL texture
      SDL_UpdateTexture(sdlTexture, NULL, pixels, 64 * sizeof(Uint32));
      // Clear screen and render
      SDL_RenderClear(renderer);
      SDL_RenderCopy(renderer, sdlTexture, NULL, NULL);
      SDL_RenderPresent(renderer);
    }

    // SDL_Delay(SLEEP_TIME_MS);
  }
  return 0;
}
