// TEST: alignas_local
// DESCRIPTION: _Alignas(N) as a local variable declaration specifier must be accepted (C11)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

int main(void) {
    _Alignas(16) char buf[64];
    buf[0] = 'A';
    (void)buf;
    printf("OK\n");
    return 0;
}
