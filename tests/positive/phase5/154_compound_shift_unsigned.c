// TEST: compound_shift_unsigned
// DESCRIPTION: >>= on unsigned/typedef unsigned must use logical shift (shrl not sarl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's P_Thrust does: angle >>= ANGLETOFINESHIFT;
   where angle is angle_t (typedef unsigned). The >>= compound
   assignment must use logical right shift (shrl). If it uses
   arithmetic shift (sarl), angles with the high bit set produce
   negative values, indexing finecosine/finesine with huge negative
   indices and causing the player to teleport randomly. */

int printf(const char *fmt, ...);

typedef unsigned angle_t;

int main(void) {
    /* >>= on typedef unsigned */
    angle_t a = 0xC0000000u;
    a >>= 19;
    /* Logical: 0xC0000000 >> 19 = 0x1800 = 6144 */
    /* Arithmetic: 0xC0000000 >> 19 = 0xFFFFF800 (negative) */
    if (a != 6144) return 1;

    /* >>= on plain unsigned int */
    unsigned int b = 0x80000000u;
    b >>= 1;
    if (b != 0x40000000u) return 2;

    /* >>= with variable shift amount */
    angle_t c = 0xF0000000u;
    int shift = 19;
    c >>= shift;
    /* 0xF0000000 >> 19 = 0x7800 = 30720 */
    if (c != 30720) return 3;

    printf("ok\n");
    return 0;
}
