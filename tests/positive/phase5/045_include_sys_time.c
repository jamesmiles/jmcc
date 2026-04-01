// TEST: include_sys_time
// DESCRIPTION: #include <sys/time.h> for struct timeval/tv_sec (Doom's i_system.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/time.h>

int printf(const char *fmt, ...);

int main(void) {
    struct timeval tv;
    tv.tv_sec = 100;
    tv.tv_usec = 500000;
    printf("ok\n");
    return 0;
}
