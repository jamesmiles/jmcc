// TEST: unsigned_cast_comparison
// DESCRIPTION: Comparison after (unsigned) cast must use unsigned comparison (setb not setl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's Z_ChangeTag does:
     if ((unsigned)block->user < 0x100)
   block->user is a void** pointer. (unsigned) truncates to 32 bits.
   The comparison must use unsigned (setb/seta) because values with
   bit 31 set (like 0xc2b3c968) are large positive unsigned numbers,
   not negative signed numbers.

   With setl (signed), 0xc2b3c968 = -1028404888 which IS < 256.
   With setb (unsigned), 0xc2b3c968 = 3266562408 which is NOT < 256.

   This causes Z_ChangeTag to falsely reject valid block owners,
   producing the intermittent "an owner is required" crash. */

int printf(const char *fmt, ...);

int main(void) {
    /* Value with bit 31 set */
    unsigned int a = 0xC0000000u;
    if (a < 0x100) return 1;  /* 3221225472 is NOT < 256 */

    /* The exact Doom pattern */
    void *ptr = (void *)0x59b8c2b3c968L;
    if ((unsigned)(long)ptr < 0x100) return 2;

    /* More cases */
    unsigned int b = 0x80000001u;
    if (b < 0x100) return 3;

    unsigned int c = 0xFFFFFFFFu;
    if (c < 0x100) return 4;

    /* Small values should still be < 0x100 */
    unsigned int d = 2;
    if (!(d < 0x100)) return 5;

    unsigned int e = 0;
    if (!(e < 0x100)) return 6;

    printf("ok\n");
    return 0;
}
