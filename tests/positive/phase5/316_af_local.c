// TEST: af_local
// DESCRIPTION: AF_LOCAL (same as AF_UNIX) must be defined in sys/socket.h (used by Redis anet.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
    int x = AF_LOCAL;
    int y = AF_UNIX;
    if (x != y) return 1;  /* AF_LOCAL == AF_UNIX */
    printf("OK\n");
    return 0;
}
