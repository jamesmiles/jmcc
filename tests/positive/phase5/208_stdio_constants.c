// TEST: stdio_constants
// DESCRIPTION: stdio.h must provide FILENAME_MAX, FOPEN_MAX and other standard constants
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite uses FILENAME_MAX to size internal path buffers.
   jmcc's stdio.h shim provides SEEK_* and BUFSIZ but lacks:
   FILENAME_MAX, FOPEN_MAX, EOF, NULL, L_tmpnam, TMP_MAX. */

#include <stdio.h>

int printf(const char *fmt, ...);

int main(void) {
    if (FILENAME_MAX <= 0) return 1;
    if (FOPEN_MAX <= 0) return 2;
    if (EOF != -1) return 3;

    char buf[FILENAME_MAX];
    buf[0] = 0;
    (void)buf;

    printf("ok\n");
    return 0;
}
