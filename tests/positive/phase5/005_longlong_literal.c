// TEST: longlong_literal
// DESCRIPTION: 64-bit integer literal exceeding 32-bit range
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 4886718345
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    long long x = 0x123456789LL;
    printf("%lld\n", x);
    return 0;
}
