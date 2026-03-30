// TEST: variadic_printf
// DESCRIPTION: Calling variadic function (printf) with many args
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1 2 3 4 5 6 7
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

int main(void) {
    printf("%d %d %d %d %d %d %d\n", 1, 2, 3, 4, 5, 6, 7);
    return 0;
}
