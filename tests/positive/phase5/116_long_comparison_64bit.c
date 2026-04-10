// TEST: long_comparison_64bit
// DESCRIPTION: Long (64-bit) relational comparisons must use cmpq not cmpl
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Same class of bug as pointer comparison (test 115): relational
   operators (<, >, <=, >=) on long values use cmpl (32-bit) instead
   of cmpq (64-bit). Values that differ only in the upper 32 bits
   compare incorrectly.

   Doom uses long for pointer arithmetic throughout the 64-bit patches
   (e.g., (long)ptr casts). Wrong long comparisons corrupt control flow. */

int printf(const char *fmt, ...);

int main(void) {
    long a = 0x100000000L;
    long b = 0x200000000L;

    /* Greater than */
    if (!(b > a)) return 1;    /* 0x200000000 > 0x100000000 */

    /* Less than */
    if (!(a < b)) return 2;

    /* Greater than or equal */
    if (a >= b) return 3;
    if (!(a >= a)) return 4;

    /* Less than or equal */
    if (b <= a) return 5;

    /* Equality (same lower 32 bits, different upper) */
    if (a == b) return 6;

    /* Inequality */
    if (!(a != b)) return 7;

    /* Long comparison in loop condition */
    long count = 0x200000000L;
    int iters = 0;
    while (count > 0) {
        count -= 0x100000000L;
        iters++;
        if (iters > 5) return 8;
    }
    if (iters != 2) return 9;

    printf("ok\n");
    return 0;
}
