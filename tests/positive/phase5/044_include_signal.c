// TEST: include_signal
// DESCRIPTION: #include <signal.h> for struct sigaction/sa_handler (Doom's i_sound.c)
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
    printf("ok\n");
    return 0;
}
