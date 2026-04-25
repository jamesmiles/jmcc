// TEST: noreturn_specifier
// DESCRIPTION: _Noreturn function specifier (C11) must be accepted (used by CPython _hashopenssl.c, _ssl.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdlib.h>

_Noreturn void die(const char *msg) {
    (void)msg;
    exit(1);
}

int main(void) {
    printf("OK\n");
    return 0;
}
