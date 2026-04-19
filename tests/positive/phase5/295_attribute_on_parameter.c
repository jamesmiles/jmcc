// TEST: attribute_on_parameter
// DESCRIPTION: __attribute__((unused)) on function parameters must be accepted and ignored
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

static int check(int x __attribute__((unused)), int y) {
    return y * 2;
}

static void noop(void *p __attribute__((unused))) { }

int main(void) {
    if (check(0, 5) != 10) return 1;
    noop(NULL);
    printf("OK\n");
    return 0;
}
