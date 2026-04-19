// TEST: sockaddr_storage
// DESCRIPTION: sys/socket.h must define struct sockaddr_storage with ss_family member (used by Redis cluster.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
    struct sockaddr_storage sa;
    sa.ss_family = AF_INET;
    if (sa.ss_family != AF_INET) return 1;
    printf("OK\n");
    return 0;
}
