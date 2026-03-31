// TEST: register_keyword
// DESCRIPTION: register keyword should be parsed and ignored
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 55
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    register int sum = 0;
    register int i;
    for (i = 1; i <= 10; i++) {
        sum += i;
    }
    printf("%d\n", sum);
    return 0;
}
