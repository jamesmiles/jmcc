// TEST: iov_max
// DESCRIPTION: IOV_MAX must be defined in limits.h when _XOPEN_SOURCE is defined (POSIX xopen extension, used by Redis networking.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#define _XOPEN_SOURCE 700
#include <limits.h>
#include <sys/uio.h>
#include <stdio.h>

int main(void) {
    int max_iov = IOV_MAX;
    if (max_iov <= 0) return 1;
    printf("OK\n");
    return 0;
}
