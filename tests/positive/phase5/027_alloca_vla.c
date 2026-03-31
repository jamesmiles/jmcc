// TEST: alloca_vla
// DESCRIPTION: Variable-length array as alloca() substitute
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: A
// STDOUT: Z
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    int n = 100;
    char buf[n];
    buf[0] = 'A';
    buf[99] = 'Z';
    printf("%c\n", buf[0]);
    printf("%c\n", buf[99]);
    return 0;
}
