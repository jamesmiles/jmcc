// TEST: longlong_multiply
// DESCRIPTION: Long long multiplication exceeding 32-bit range (Doom fixed-point math)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 10000000000
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    long long a = 100000LL;
    long long b = 100000LL;
    long long c = a * b;
    printf("%lld\n", c);
    return 0;
}
