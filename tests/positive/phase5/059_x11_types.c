// TEST: x11_types
// DESCRIPTION: X11 types needed by Doom's i_video.c (Visual, Colormap, GC, XEvent, etc.)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    Display *dpy;
    Window win;
    Visual *vis;
    Colormap cmap;
    GC gc;
    XEvent event;
    XVisualInfo vinfo;
    XImage *img;

    dpy = 0;
    win = 0;
    vis = 0;
    cmap = 0;
    gc = 0;
    img = 0;
    printf("ok\n");
    return 0;
}
