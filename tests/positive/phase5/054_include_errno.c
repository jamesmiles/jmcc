// TEST: include_errno
// DESCRIPTION: #include <errno.h> for EWOULDBLOCK/errno (Doom's i_net.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <errno.h>

int printf(const char *fmt, ...);

int main(void) {
    int e = EWOULDBLOCK;
    printf("ok\n");
    return 0;
}
