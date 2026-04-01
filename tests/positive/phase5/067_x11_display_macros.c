// TEST: x11_display_macros
// DESCRIPTION: X11 Display access macros: DefaultScreen, RootWindow, GCFunction
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>

int printf(const char *fmt, ...);

int main(void) {
    /* GCFunction is a GC value mask constant */
    long gcf = GCFunction;

    /* DefaultScreen and RootWindow are macros taking Display* arg.
       In real Xlib: #define DefaultScreen(dpy) ((dpy)->default_screen)
       Doom uses: DefaultScreen(X_display), RootWindow(X_display, ...) */
    Display *dpy = 0;
    int screen = DefaultScreen(dpy);
    unsigned long root = RootWindow(dpy, screen);

    printf("ok\n");
    return 0;
}
