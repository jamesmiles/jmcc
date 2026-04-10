// TEST: pointer_truthiness_64bit
// DESCRIPTION: Pointer truthiness check must test all 64 bits, not just lower 32
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* z_zone.c's Z_Malloc has: while (base->user || base->size < size)
   base->user is void** (a pointer). The truthiness check (!ptr)
   must test the full 64-bit value. If it only checks the lower
   32 bits (via cmpl $0, %eax instead of cmpq $0, %rax), a pointer
   like 0x000000XX00000000 appears as NULL, causing the allocator
   to treat an in-use block as free and hand it out again.

   This produces intermittent crashes because it only fails when
   ASLR places pointers with zero in the lower 32 bits. */

int printf(const char *fmt, ...);

struct block {
    int size;
    void **user;
    int tag;
    int id;
    struct block *next;
    struct block *prev;
};

int main(void) {
    struct block b;

    /* Pointer with zero low 32 bits, non-zero high bits */
    b.user = (void **)0x100000000L;
    if (!b.user) return 1;  /* FAILS: treated as NULL */

    /* Higher address */
    b.user = (void **)0x7fff00000000L;
    if (!b.user) return 2;

    /* NULL must still be falsy */
    b.user = 0;
    if (b.user) return 3;

    /* Small non-NULL pointer (like Doom's (void*)2) */
    b.user = (void **)2;
    if (!b.user) return 4;

    /* Pointer field in conditional expression */
    b.user = (void **)0x200000000L;
    int result = b.user ? 1 : 0;
    if (result != 1) return 5;

    /* Pointer in while condition (the actual Doom pattern) */
    b.user = (void **)0x300000000L;
    b.size = 100;
    int count = 0;
    while (b.user || b.size < 50) {
        b.user = 0;  /* would loop forever if first check fails */
        count++;
        if (count > 1) return 6;
    }

    printf("ok\n");
    return 0;
}
