// TEST: msghdr_members
// DESCRIPTION: struct msghdr must have msg_name, msg_namelen, msg_iov, msg_iovlen, msg_control, msg_controllen, msg_flags in sys/socket.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <stdio.h>

int main(void) {
    struct msghdr msg;
    msg.msg_name = (void *)0;
    msg.msg_namelen = 0;
    msg.msg_iov = (void *)0;
    msg.msg_iovlen = 0;
    msg.msg_control = (void *)0;
    msg.msg_controllen = 0;
    msg.msg_flags = 0;
    (void)msg;
    printf("OK\n");
    return 0;
}
