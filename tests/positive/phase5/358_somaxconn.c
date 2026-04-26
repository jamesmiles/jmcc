// TEST: somaxconn
// DESCRIPTION: SOMAXCONN must be defined in sys/socket.h (used by CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
    int n = SOMAXCONN;
    if (n <= 0) return 1;
    printf("OK\n");
    return 0;
}
