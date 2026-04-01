// TEST: include_sys_ioctl
// DESCRIPTION: #include <sys/ioctl.h> for FIONBIO (Doom's i_net.c non-blocking IO)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/ioctl.h>

int printf(const char *fmt, ...);

int main(void) {
    unsigned long req = FIONBIO;
    printf("ok\n");
    return 0;
}
