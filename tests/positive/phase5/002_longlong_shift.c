// TEST: longlong_shift
// DESCRIPTION: 64-bit shift operations (Doom's >> FRACBITS pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1099511627776
// STDOUT: 16777216
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    long long x = 1LL << 40;
    long long y = x >> 16;
    printf("%lld\n", x);
    printf("%lld\n", y);
    return 0;
}
