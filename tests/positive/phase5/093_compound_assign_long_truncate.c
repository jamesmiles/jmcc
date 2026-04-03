// TEST: compound_assign_long_truncate
// DESCRIPTION: Compound assignment on long must use 64-bit operations, not 32-bit
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Compound assignments (+=, -=, etc.) always use movl for load and
   store of non-pointer types, truncating long/long long values to
   32 bits. Regular assignment (=) correctly uses movq for 8-byte types.

   Doom's 64-bit patches use (long) casts for pointer arithmetic.
   Any compound assignment on a long variable loses the upper 32 bits,
   which is especially problematic with ASLR where addresses use
   all 48 bits of the virtual address space. */

int printf(const char *fmt, ...);

int main(void) {
    /* Test 1: long compound add preserves upper 32 bits */
    long x = 0x100000000L;  /* bit 32 set */
    x += 1;

    if (x != 0x100000001L) return 1;  /* FAILS if truncated to 32-bit: x = 1 */

    /* Test 2: long compound subtract */
    long y = 0x200000005L;
    y -= 3;

    if (y != 0x200000002L) return 2;

    /* Test 3: long compound OR */
    long z = 0x300000000L;
    z |= 0xFF;

    if (z != 0x3000000FFL) return 3;

    /* Test 4: long compound shift */
    long w = 1L;
    w <<= 33;

    if (w != 0x200000000L) return 4;

    printf("ok\n");
    return 0;
}
