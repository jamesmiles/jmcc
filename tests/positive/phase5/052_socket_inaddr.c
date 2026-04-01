// TEST: socket_inaddr
// DESCRIPTION: INADDR_ANY and struct sockaddr_in (Doom's i_net.c networking)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/socket.h>
#include <netinet/in.h>

int printf(const char *fmt, ...);

int main(void) {
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = 0;
    printf("ok\n");
    return 0;
}
