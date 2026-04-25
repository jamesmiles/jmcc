// TEST: si_user
// DESCRIPTION: SI_USER must be defined in signal.h (used by Redis debug.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <signal.h>
#include <stdio.h>

int main(void) {
    int code = SI_USER;
    (void)code;
    printf("OK\n");
    return 0;
}
