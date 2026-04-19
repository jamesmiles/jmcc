// TEST: ipv6_socket_structs
// DESCRIPTION: netinet/in.h must define struct sockaddr_in6, struct in6_addr, AF_INET6, and in6addr_any (used by Redis anet.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    struct sockaddr_in6 sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin6_family = AF_INET6;
    sa.sin6_port = 80;
    sa.sin6_addr = in6addr_any;
    (void)AF_INET6;
    printf("OK\n");
    return 0;
}
