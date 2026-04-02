// TEST: xcolor_members
// DESCRIPTION: XColor struct needs red/green/blue/pixel/flags members (Doom's i_video.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    XColor color;
    color.pixel = 0;
    color.red = 0;
    color.green = 0;
    color.blue = 0;
    color.flags = 04;
    printf("ok\n");
    return 0;
}
