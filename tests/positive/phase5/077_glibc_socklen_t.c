// TEST: glibc_socklen_t
// DESCRIPTION: Full i_net.c system header chain exposing __socklen_t issue
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's i_net.c system header chain. The combination causes
   __socklen_t to not be defined when socklen_t typedef is reached. */
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/ioctl.h>

int printf(const char *fmt, ...);

int main(void) {
    socklen_t len = sizeof(int);
    printf("ok\n");
    return 0;
}
