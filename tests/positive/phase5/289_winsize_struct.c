// TEST: winsize_struct
// DESCRIPTION: struct winsize with ws_row/ws_col must be in sys/ioctl.h (used by Redis memtest.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main(void) {
    struct winsize ws;
    /* ioctl may fail in CI but struct must be usable */
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0) {
        (void)ws.ws_col;
        (void)ws.ws_row;
    }
    printf("OK\n");
    return 0;
}
