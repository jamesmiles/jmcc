// TEST: sock_cloexec
// DESCRIPTION: SOCK_CLOEXEC must be defined in sys/socket.h (used by Redis anet.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
    int flags = SOCK_CLOEXEC;
    if (flags <= 0) return 1;
    printf("OK\n");
    return 0;
}
