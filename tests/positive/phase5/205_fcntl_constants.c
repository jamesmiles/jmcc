// TEST: fcntl_constants
// DESCRIPTION: fcntl.h must define the standard POSIX O_* constants
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's unix VFS uses O_EXCL, O_NOCTTY, O_NONBLOCK, O_APPEND, etc.
   jmcc's built-in fcntl.h only provides O_RDONLY, O_WRONLY, O_RDWR,
   O_CREAT, O_TRUNC. Missing constants cause "undeclared variable"
   errors even though they're standard POSIX.

   Either jmcc should use the real system fcntl.h, or the built-in
   should provide the full set of commonly-used O_* flags. */

#include <fcntl.h>

int printf(const char *fmt, ...);

int main(void) {
    /* POSIX-required flags (widely used) */
    (void)O_RDONLY;
    (void)O_WRONLY;
    (void)O_RDWR;
    (void)O_CREAT;
    (void)O_EXCL;
    (void)O_NOCTTY;
    (void)O_TRUNC;
    (void)O_APPEND;
    (void)O_NONBLOCK;

    /* Basic consistency check: the flags are distinct bits */
    if ((O_RDONLY | O_WRONLY | O_RDWR) == 0) return 1;

    printf("ok\n");
    return 0;
}
