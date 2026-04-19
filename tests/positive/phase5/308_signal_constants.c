// TEST: signal_constants
// DESCRIPTION: signal.h must define SIGBUS, SIG_BLOCK, SIG_UNBLOCK, SIG_SETMASK, and sigset_t (used by Redis)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <signal.h>
#include <stdio.h>

int main(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGBUS);
    int r = sigprocmask(SIG_BLOCK, &mask, NULL);
    sigprocmask(SIG_SETMASK, &mask, NULL);
    (void)SIG_UNBLOCK;
    (void)r;
    printf("OK\n");
    return 0;
}
