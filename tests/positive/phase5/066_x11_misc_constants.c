// TEST: x11_misc_constants
// DESCRIPTION: Remaining X11 constants/macros for Doom's i_video.c
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    /* GC function */
    int gc = GXclear;

    /* X11 macros that access Display members */
    /* In real Xlib these are macros like #define DefaultScreen(dpy) ...
       Doom uses: DefaultScreen, RootWindow, BlackPixel, DefaultVisual */

    /* None is used as a null resource ID */
    int n = None;

    printf("ok\n");
    return 0;
}
