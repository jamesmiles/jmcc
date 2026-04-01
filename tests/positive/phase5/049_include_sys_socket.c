// TEST: include_sys_socket
// DESCRIPTION: #include <sys/socket.h> for SOCK_DGRAM/socket types (Doom's i_net.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/socket.h>

int printf(const char *fmt, ...);

int main(void) {
    int type = SOCK_DGRAM;
    printf("ok\n");
    return 0;
}
