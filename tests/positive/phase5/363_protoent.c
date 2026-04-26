// TEST: protoent
// DESCRIPTION: struct protoent with p_name, p_aliases, p_proto must be in netdb.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netdb.h>
#include <stdio.h>

int main(void) {
    struct protoent pe;
    pe.p_name = "tcp";
    pe.p_proto = 6;
    (void)pe;
    printf("OK\n");
    return 0;
}
