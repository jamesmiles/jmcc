// TEST: h_errno
// DESCRIPTION: h_errno must be available from netdb.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netdb.h>
#include <stdio.h>

int main(void) {
    int e = h_errno;
    (void)e;
    printf("OK\n");
    return 0;
}
