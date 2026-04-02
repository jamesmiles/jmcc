// TEST: x11_visual_constants
// DESCRIPTION: X11 visual class and color flag constants (Doom's i_video.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    /* Visual class constants */
    int vc = PseudoColor;

    /* Color flags for XColor */
    int flags = DoRed | DoGreen | DoBlue;

    printf("ok\n");
    return 0;
}
