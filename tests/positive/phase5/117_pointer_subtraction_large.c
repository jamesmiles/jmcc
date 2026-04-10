// TEST: pointer_subtraction_large
// DESCRIPTION: Pointer subtraction must produce correct 64-bit result for distant pointers
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* ptr1 - ptr2 for char pointers is a ptrdiff_t (64-bit on x86-64).
   If the subtraction uses 32-bit subq or the result is truncated
   to 32 bits, differences > 4GB are wrong. */

int printf(const char *fmt, ...);

int main(void) {
    /* Pointers far apart */
    char *a = (char *)0x200000000L;
    char *b = (char *)0x100000000L;
    long diff = a - b;
    if (diff != 0x100000000L) return 1;

    /* Negative difference */
    diff = b - a;
    if (diff != -0x100000000L) return 2;

    /* Closer pointers (should still work) */
    char *c = (char *)0x100000010L;
    char *d = (char *)0x100000000L;
    diff = c - d;
    if (diff != 16) return 3;

    /* Struct pointer subtraction (divides by sizeof) */
    struct foo { long x; long y; };  /* 16 bytes */
    struct foo *s1 = (struct foo *)0x200000000L;
    struct foo *s2 = (struct foo *)0x100000000L;
    long sdiff = s1 - s2;
    /* (0x200000000 - 0x100000000) / 16 = 0x10000000 */
    if (sdiff != 0x10000000L) return 4;

    printf("ok\n");
    return 0;
}
