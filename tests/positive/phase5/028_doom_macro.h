#ifndef DOOM_MACRO_H
#define DOOM_MACRO_H

typedef unsigned char byte;

typedef struct memblock_s {
    int id;
    int tag;
    int size;
    void *user;
    struct memblock_s *prev;
    struct memblock_s *next;
} memblock_t;

void Z_ChangeTag2(void *ptr, int tag);

#define ZONEID 0x1d4a11

#define Z_ChangeTag(p,t) \
{ \
      if (( (memblock_t *)( (byte *)(p) - sizeof(memblock_t)))->id!=ZONEID) \
          printf("Z_CT at %s:%i\n", __FILE__, __LINE__); \
      Z_ChangeTag2(p,t); \
};

#endif
