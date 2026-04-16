// TEST: unistd_sysconf
// DESCRIPTION: unistd.h must provide sysconf() and _SC_* constants
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite queries the system page size via sysconf(_SC_PAGESIZE)
   for memory-mapped file alignment. jmcc's built-in unistd.h
   lacks sysconf() and the _SC_* constant family. */

#include <unistd.h>

int printf(const char *fmt, ...);

int main(void) {
    long page = sysconf(_SC_PAGESIZE);
    if (page <= 0) return 1;

    /* Also commonly used */
    (void)_SC_OPEN_MAX;
    (void)_SC_NPROCESSORS_ONLN;

    printf("ok\n");
    return 0;
}
