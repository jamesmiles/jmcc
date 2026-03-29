// TEST: printf_format
// DESCRIPTION: Printf with various format specifiers
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: num=42 hex=0x2a char=A str=hello
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

int main(void) {
    printf("num=%d hex=0x%x char=%c str=%s\n", 42, 42, 65, "hello");
    return 0;
}
