// TEST: include_netinet_in
// DESCRIPTION: #include <netinet/in.h> for IPPROTO_UDP (Doom's i_net.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <netinet/in.h>

int printf(const char *fmt, ...);

int main(void) {
    int proto = IPPROTO_UDP;
    printf("ok\n");
    return 0;
}
