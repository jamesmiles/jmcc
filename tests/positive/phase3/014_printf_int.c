// TEST: printf_int
// DESCRIPTION: Print an integer with printf
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 42
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 7.21.6.1 (The fprintf function)

int printf(const char *fmt, ...);

int main(void) {
    printf("%d\n", 42);
    return 0;
}
