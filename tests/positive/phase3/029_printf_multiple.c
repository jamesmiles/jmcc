// TEST: printf_multiple
// DESCRIPTION: Printf with multiple arguments
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1 + 2 = 3
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

int main(void) {
    int a = 1;
    int b = 2;
    printf("%d + %d = %d\n", a, b, a + b);
    return 0;
}
