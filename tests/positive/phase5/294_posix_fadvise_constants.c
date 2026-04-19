// TEST: posix_fadvise_constants
// DESCRIPTION: POSIX_FADV_DONTNEED and other posix_fadvise constants must be defined
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <fcntl.h>

int main(void) {
    int a = POSIX_FADV_DONTNEED;
    int b = POSIX_FADV_SEQUENTIAL;
    int c = POSIX_FADV_WILLNEED;
    (void)a; (void)b; (void)c;
    printf("OK\n");
    return 0;
}
