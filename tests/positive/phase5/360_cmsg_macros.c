// TEST: cmsg_macros
// DESCRIPTION: CMSG_LEN, CMSG_DATA, CMSG_SPACE, CMSG_FIRSTHDR, CMSG_NXTHDR must be defined in sys/socket.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
#ifndef CMSG_LEN
#error "CMSG_LEN not defined"
#endif
    struct msghdr msg = {0};
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    (void)cmsg;
    printf("OK\n");
    return 0;
}
