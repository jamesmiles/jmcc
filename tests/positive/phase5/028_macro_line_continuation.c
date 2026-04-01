// TEST: macro_line_continuation
// DESCRIPTION: Multi-line macro from header with casts and pointer math (Doom Z_ChangeTag)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: tag changed to 5
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

#include "028_doom_macro.h"

int changed_tag = 0;

void Z_ChangeTag2(void *ptr, int tag) {
    changed_tag = tag;
}

int main(void) {
    /* Allocate space for memblock header + payload */
    byte storage[sizeof(memblock_t) + 16];
    memblock_t *block = (memblock_t *)storage;
    block->id = ZONEID;
    block->tag = 0;

    /* ptr points past the header, like Doom's Z_Malloc returns */
    void *ptr = (void *)(storage + sizeof(memblock_t));

    Z_ChangeTag(ptr, 5);
    printf("tag changed to %d\n", changed_tag);
    return 0;
}
