// TEST: typedef_unsigned_shift
// DESCRIPTION: Right shift on typedef unsigned must use logical shift (shrl), not arithmetic (sarl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's angle computation:
     typedef unsigned angle_t;
     angle1 = (angle1 + ANG90) >> ANGLETOFINESHIFT;

   (angle_t + 0x40000000u) >> 19 must use logical right shift.
   With arithmetic shift, 0xC0000001 >> 19 = -2048 (0xFFFFF800)
   instead of 6144 (0x1800). This produces an out-of-bounds
   index into viewangletox[], crashing R_AddLine.

   Test 109 fixed unsigned int >> but typedef unsigned may use
   a different code path that still uses sarl. */

int printf(const char *fmt, ...);

typedef unsigned angle_t;

int main(void) {
    /* Basic typedef unsigned shift */
    angle_t a = 0x80000000u;
    angle_t b = a >> 1;
    if (b != 0x40000000u) return 1;  /* logical: 0x40000000 */

    /* The Doom pattern */
    angle_t angle = 0xC0000001u;
    angle_t shifted = angle >> 19;
    /* 0xC0000001 >> 19 logical = 6144 */
    if (shifted != 6144) return 2;

    /* After addition that wraps */
    angle_t ang = 0xC0000000u;
    angle_t result = (ang + 0x40000000u) >> 19;
    /* 0xC0000000 + 0x40000000 = 0x100000000 wraps to 0 */
    /* 0 >> 19 = 0 */
    if (result != 0) return 3;

    /* Another case */
    ang = 0x80000001u;
    result = (ang + 0x40000000u) >> 19;
    /* 0x80000001 + 0x40000000 = 0xC0000001 */
    /* 0xC0000001 >> 19 = 6144 */
    if (result != 6144) return 4;

    printf("ok\n");
    return 0;
}
