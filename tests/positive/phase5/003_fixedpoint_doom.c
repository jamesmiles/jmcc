// TEST: fixedpoint_doom
// DESCRIPTION: Doom's FixedMul pattern: ((long long)a * (long long)b) >> FRACBITS
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 196608
// STDOUT: 65536
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int FixedMul(int a, int b) {
    return (int)(((long long)a * (long long)b) >> 16);
}

int main(void) {
    int a = 0x10000;  /* 1.0 in 16.16 fixed point */
    int b = 0x30000;  /* 3.0 */
    int result = FixedMul(a, b);
    printf("%d\n", result);  /* should be 0x30000 = 196608 */

    result = FixedMul(0x10000, 0x10000);  /* 1.0 * 1.0 = 1.0 */
    printf("%d\n", result);  /* should be 0x10000 = 65536 */
    return 0;
}
