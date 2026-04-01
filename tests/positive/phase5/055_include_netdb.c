// TEST: include_netdb
// DESCRIPTION: struct hostent h_addr_list member from <netdb.h> (Doom's i_net.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <netdb.h>

int printf(const char *fmt, ...);

int main(void) {
    struct hostent he;
    he.h_addr_list = 0;
    printf("ok\n");
    return 0;
}
