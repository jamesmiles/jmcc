// TEST: x11_struct_members
// DESCRIPTION: XSetWindowAttributes and XVisualInfo struct members (Doom's i_video.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>
#include <X11/Xutil.h>

int printf(const char *fmt, ...);

int main(void) {
    /* XSetWindowAttributes members used by Doom */
    XSetWindowAttributes attribs;
    attribs.border_pixel = 0;
    attribs.colormap = 0;
    attribs.event_mask = 0;

    /* XVisualInfo members used by Doom */
    XVisualInfo vinfo;
    vinfo.visual = 0;
    vinfo.depth = 8;

    printf("ok\n");
    return 0;
}
