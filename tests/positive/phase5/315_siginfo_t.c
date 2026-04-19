// TEST: siginfo_t
// DESCRIPTION: siginfo_t struct must have si_addr and si_code members, and SA_SIGINFO flag must be defined (used by Redis debug.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <signal.h>
#include <stdio.h>

static void handler(int sig, siginfo_t *info, void *ctx) {
    void *addr = info->si_addr;
    int code = info->si_code;
    (void)sig; (void)addr; (void)code; (void)ctx;
}

int main(void) {
    struct sigaction sa;
    sa.sa_sigaction = handler;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    printf("OK\n");
    return 0;
}
