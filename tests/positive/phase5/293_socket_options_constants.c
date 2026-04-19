// TEST: socket_options_constants
// DESCRIPTION: SO_ERROR, SO_KEEPALIVE, SO_REUSEADDR etc. must be in sys/socket.h
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <sys/socket.h>

int main(void) {
    /* These constants must be defined */
    int a = SO_ERROR;
    int b = SO_KEEPALIVE;
    int c = SO_REUSEADDR;
    (void)a; (void)b; (void)c;
    printf("OK\n");
    return 0;
}
