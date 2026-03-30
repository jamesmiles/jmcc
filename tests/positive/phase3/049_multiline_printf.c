// TEST: multiline_printf
// DESCRIPTION: Printf with escape sequences producing multiple lines
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: Line 1
// STDOUT: Line 2
// STDOUT: Line 3
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

int main(void) {
    printf("Line 1\nLine 2\nLine 3\n");
    return 0;
}
