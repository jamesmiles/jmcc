// TEST: longlong_cast_signextend
// DESCRIPTION: Cast int to long long with sign extension (movslq)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -1
// STDOUT: 1
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    int x = -1;
    long long y = (long long)x;
    printf("%lld\n", y);          /* should be -1, not 4294967295 */
    printf("%d\n", y == -1LL);    /* should be 1 (true) */
    return 0;
}
