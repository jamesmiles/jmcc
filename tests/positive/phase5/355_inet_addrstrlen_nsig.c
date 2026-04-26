// TEST: inet_addrstrlen_nsig
// DESCRIPTION: INET_ADDRSTRLEN must be defined in netinet/in.h and _NSIG must be defined in signal.h (CPython socketmodule.c, _posixsubprocess.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>

int main(void) {
    int a = INET_ADDRSTRLEN;
    int b = _NSIG;
    if (a <= 0 || b <= 0) return 1;
    printf("OK\n");
    return 0;
}
