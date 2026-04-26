// TEST: attribute_aligned_local_var
// DESCRIPTION: __attribute__((aligned(N))) on a local variable declarator must be accepted (used by CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

int main(void) {
    char buf[256] __attribute__((aligned(8)));
    int x __attribute__((aligned(4))) = 42;
    buf[0] = 'O'; buf[1] = 'K'; buf[2] = '\0';
    if (x != 42) return 1;
    printf("%s\n", buf);
    return 0;
}
