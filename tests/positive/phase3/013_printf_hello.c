// TEST: printf_hello
// DESCRIPTION: Call printf to output a string (requires libc)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: Hello, World!
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 7.21.6.1 (The fprintf function)

int printf(const char *fmt, ...);

int main(void) {
    printf("Hello, World!\n");
    return 0;
}
