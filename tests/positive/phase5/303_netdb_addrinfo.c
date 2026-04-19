// TEST: netdb_addrinfo
// DESCRIPTION: netdb.h must define struct addrinfo and AI_* constants (AI_NUMERICHOST, AI_PASSIVE, AI_CANONNAME, AI_NUMERICSERV)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <netdb.h>
#include <string.h>

int main(void) {
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_flags = AI_NUMERICHOST | AI_PASSIVE;
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    (void)AI_CANONNAME;
    (void)AI_NUMERICSERV;
    printf("OK\n");
    return 0;
}
