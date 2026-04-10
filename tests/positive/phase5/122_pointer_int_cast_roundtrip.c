// TEST: pointer_int_cast_roundtrip
// DESCRIPTION: Pointer to long cast and back must preserve all 64 bits
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's 64-bit patches use (long)ptr for pointer arithmetic and
   offsetof patterns. The cast must preserve all 48+ address bits. */

int printf(const char *fmt, ...);

char buf[256];

int main(void) {
    /* 1. Pointer -> long -> pointer roundtrip */
    char *p = &buf[128];
    long l = (long)p;
    char *back = (char *)l;
    if (back != p) return 1;

    /* 2. Arithmetic on casted pointer */
    long addr = (long)&buf[0];
    long addr2 = addr + 100;
    char *p2 = (char *)addr2;
    if (p2 != &buf[100]) return 2;

    /* 3. Difference via long cast (Doom's offsetof pattern) */
    long base = (long)&buf[0];
    long field = (long)&buf[64];
    long offset = field - base;
    if (offset != 64) return 3;

    /* 4. Alignment check via cast (common C pattern) */
    long aligned = ((long)&buf[7]) & ~7L;
    /* Should be &buf[0] aligned down to 8 */
    if (aligned % 8 != 0) return 4;

    /* 5. Casting int to pointer (must zero-extend, not sign-extend) */
    int small = 0x1000;
    void *sp = (void *)(long)small;
    if ((long)sp != 0x1000L) return 5;

    /* 6. Casting negative int to pointer via long */
    int neg = -1;
    long neg_long = (long)neg;  /* sign-extend to 0xFFFFFFFFFFFFFFFF */
    if (neg_long != -1L) return 6;

    printf("ok\n");
    return 0;
}
