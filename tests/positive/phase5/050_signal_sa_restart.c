// TEST: signal_sa_restart
// DESCRIPTION: SA_RESTART flag from signal.h (Doom's i_sound.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <signal.h>

int printf(const char *fmt, ...);

void handler(int sig) { (void)sig; }

int main(void) {
    struct sigaction sa;
    sa.sa_handler = handler;
    sa.sa_flags = SA_RESTART;
    printf("ok\n");
    return 0;
}
