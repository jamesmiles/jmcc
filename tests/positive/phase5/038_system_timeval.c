// TEST: system_timeval
// DESCRIPTION: struct timeval with tv_sec/tv_usec (Doom's i_system.c timing)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: sec=100
// STDOUT: usec=500000
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom's i_system.c uses gettimeofday() with struct timeval.
   This requires <sys/time.h>. */
typedef long time_t;
typedef long suseconds_t;

struct timeval {
    time_t tv_sec;
    suseconds_t tv_usec;
};

int main(void) {
    struct timeval tv;
    tv.tv_sec = 100;
    tv.tv_usec = 500000;
    printf("sec=%ld\n", tv.tv_sec);
    printf("usec=%ld\n", tv.tv_usec);
    return 0;
}
