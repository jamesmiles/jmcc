// TEST: hex_shift
// DESCRIPTION: Byte extraction via shift and mask (Doom color/lookup patterns)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 171
// STDOUT: 3072
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    int x = 0xABCD;

    /* Extract high byte */
    int hi = (x >> 8) & 0xFF;
    printf("%d\n", hi);  /* 0xAB = 171 */

    /* Shift nibble */
    int shifted = (x & 0xF0) << 4;
    printf("%d\n", shifted);  /* 0xC0 << 4 = 0xC00 = 3072 */

    return 0;
}
