// TEST: ptr_negative_offset
// DESCRIPTION: Pointer + negative int must sign-extend the int before 64-bit addition
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* ptr + (-4) requires the int -4 to be sign-extended to 64-bit
   (0xFFFFFFFFFFFFFFFC) before adding to the pointer. If it's
   zero-extended instead (0x00000000FFFFFFFC), the result is
   ptr + 4294967292 instead of ptr - 4. */

int printf(const char *fmt, ...);

int main(void) {
    char *base = (char *)0x100000000L;

    /* Negative constant offset */
    char *r = base + (-4);
    if (r != (char *)0x0FFFFFFFCL) return 1;

    /* Negative variable offset */
    int off = -16;
    r = base + off;
    if (r != (char *)(0x100000000L - 16)) return 2;

    /* Subtraction (should work since it's explicit) */
    r = base - 4;
    if (r != (char *)0x0FFFFFFFCL) return 3;

    /* Array indexing with negative (like Doom's mousebuttons[-1]) */
    char arr[32];
    char *mid = &arr[16];
    mid[-1] = 42;
    if (arr[15] != 42) return 4;

    printf("ok\n");
    return 0;
}
