// TEST: x11_display
// DESCRIPTION: X11 headers for Display/Window types (Doom's i_video.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's i_video.c requires X11 headers. JMCC needs builtin stubs
   or the ability to process X11/Xlib.h from the system. */
#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    Display *dpy;
    dpy = 0;
    printf("ok\n");
    return 0;
}
