// TEST: sig_atomic_t
// DESCRIPTION: sig_atomic_t must be defined in signal.h (used by Lua lstate.h and lapi.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <signal.h>

volatile sig_atomic_t flag = 0;

void handler(int sig) { flag = 1; (void)sig; }

int main(void) {
    flag = 42;
    if (flag != 42) return 1;
    printf("OK\n");
    return 0;
}
