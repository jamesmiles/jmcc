#ifndef __TEST_ZONE__
#define __TEST_ZONE__

#include <stdio.h>

#define TAG_STATIC 1
#define TAG_CACHE  101

void* TZ_Malloc(int size, int tag, void *ptr);
void  TZ_Free(void *ptr);
void  TZ_ChangeTag2(void *ptr, int tag);

typedef struct tblock_s
{
    int			size;	// including the header
    void**		user;	// NULL if a free block
    int			tag;	// purgelevel
    int			id;	// should be ZONEID
    struct tblock_s*	next;
    struct tblock_s*	prev;
} tblock_t;

#define TZ_ChangeTag(p,t) \
{ \
    if (((tblock_t *)((char *)(p) - sizeof(tblock_t)))->id != 0x1d4a11) \
        return; \
    TZ_ChangeTag2(p,t); \
};

#endif
