// TEST: printf_string_var
// DESCRIPTION: Print a string variable using printf
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: Hello from JMCC!
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

int main(void) {
    char *msg = "Hello from JMCC!";
    printf("%s\n", msg);
    return 0;
}
