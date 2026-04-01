// TEST: xevent_members
// DESCRIPTION: XEvent union members used by Doom (xkey, xbutton, xmotion, xexpose)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    XEvent event;
    int t = event.type;

    /* Doom accesses these XEvent union members */
    event.xkey.keycode = 0;
    event.xbutton.button = 1;
    event.xmotion.x = 100;
    event.xmotion.y = 200;
    event.xexpose.count = 0;

    printf("ok\n");
    return 0;
}
