// TEST: servent
// DESCRIPTION: struct servent with s_name, s_aliases, s_port, s_proto must be in netdb.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netdb.h>
#include <stdio.h>

int main(void) {
    struct servent se;
    se.s_name = "http";
    se.s_port = 80;
    se.s_proto = "tcp";
    (void)se;
    printf("OK\n");
    return 0;
}
