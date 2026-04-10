// TEST: void_ptr_ptr_write
// DESCRIPTION: Writing through void** must store a full 8-byte pointer, not 4 bytes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's zone allocator (z_zone.c) does:
     *(void **)user = (void *)((byte *)base + sizeof(memblock_t));
   This writes a pointer value through a void** indirection.
   If the store uses movl (4 bytes) instead of movq (8 bytes),
   only the lower 32 bits of the pointer are written, corrupting
   the upper 32 bits. With ASLR, pointers use all 48 bits, so
   the corrupted pointer causes intermittent crashes.

   Also tests: *block->user = 0  (clearing a pointer through void**) */

int printf(const char *fmt, ...);

int main(void) {
    char buf[100];
    char *ptr = 0;

    /* Pattern 1: *(void **)&ptr = &buf[50] */
    void **indirect = (void **)&ptr;
    *indirect = (void *)&buf[50];

    if (ptr != &buf[50]) return 1;

    /* Pattern 2: write through struct member (void** user) */
    struct block {
        int size;
        void **user;
        int tag;
    };

    char *target = 0;
    struct block b;
    b.user = (void **)&target;

    /* Doom pattern: *(void **)user = (void *)pointer */
    *(void **)b.user = (void *)&buf[75];
    if (target != &buf[75]) return 2;

    /* Pattern 3: clear through void** (*block->user = 0) */
    *b.user = 0;
    if (target != 0) return 3;

    /* Pattern 4: high pointer value (ASLR-sensitive) */
    char *high_ptr = (char *)0x7fff12345678L;
    void **hp = (void **)&ptr;
    *hp = (void *)high_ptr;
    if (ptr != high_ptr) return 4;

    printf("ok\n");
    return 0;
}
