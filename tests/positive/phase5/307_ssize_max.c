// TEST: ssize_max
// DESCRIPTION: SSIZE_MAX must be defined in limits.h (POSIX extension, used by CPython modsupport.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <limits.h>
#include <stdio.h>

int main(void) {
    long s = SSIZE_MAX;
    if (s <= 0) return 1;
    printf("OK\n");
    return 0;
}
