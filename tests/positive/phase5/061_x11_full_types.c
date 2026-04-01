// TEST: x11_full_types
// DESCRIPTION: All X11 types and keysyms needed by Doom's i_video.c
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <X11/extensions/XShm.h>

int printf(const char *fmt, ...);

int main(void) {
    /* Types from Xlib.h */
    Cursor cursor;
    Pixmap pixmap;
    XGCValues xgc;
    XColor color;
    XSetWindowAttributes attr;
    XWindowAttributes wattr;
    KeySym key;
    Atom atom;

    /* Keysyms from keysym.h */
    int k = XK_Escape;

    /* XShm types */
    XShmSegmentInfo shminfo;

    /* XUtil types */
    XSizeHints hints;

    cursor = 0;
    pixmap = 0;
    key = XK_Return;
    atom = 0;
    printf("ok\n");
    return 0;
}
