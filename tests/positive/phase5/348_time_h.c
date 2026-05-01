// TEST: time_h
// DESCRIPTION: <time.h> must declare time_t / struct tm / time() / strftime()
// so loslib.c-style usage parses. Repro from Lua loslib.c l_checktime.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// PHASE: 5

#include <stdio.h>
#include <time.h>

static time_t l_checktime(long t) {
    return (time_t)t;
}

int main(void) {
    time_t now = time(NULL);
    (void)now;
    struct tm tm;
    tm.tm_sec = 0;
    tm.tm_year = 100;
    char buf[64];
    /* Just confirm strftime is callable; output value not checked here. */
    (void)strftime(buf, sizeof(buf), "%Y", &tm);
    (void)l_checktime(1234567890L);
    printf("ok\n");
    return 0;
}
