// TEST: itimerval
// DESCRIPTION: struct itimerval with it_interval/it_value (Doom's i_sound.c timer)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/time.h>

int printf(const char *fmt, ...);

int main(void) {
    struct itimerval timer;
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 10000;
    timer.it_value.tv_sec = 0;
    timer.it_value.tv_usec = 10000;
    printf("ok\n");
    return 0;
}
