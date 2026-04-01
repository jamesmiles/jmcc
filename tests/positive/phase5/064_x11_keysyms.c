// TEST: x11_keysyms
// DESCRIPTION: X11 keysym constants from <X11/keysym.h> (Doom's i_video.c key mapping)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/keysym.h>

int printf(const char *fmt, ...);

int main(void) {
    /* All keysyms used by Doom's i_video.c */
    int keys[] = {
        XK_space, XK_Return, XK_Escape, XK_Tab, XK_BackSpace, XK_Delete,
        XK_Pause, XK_equal, XK_minus, XK_asciitilde,
        XK_Shift_L, XK_Shift_R, XK_Control_L, XK_Control_R,
        XK_Alt_L, XK_Alt_R, XK_Meta_L, XK_Meta_R,
        XK_Left, XK_Right, XK_Up, XK_Down,
        XK_F1, XK_F2, XK_F3, XK_F4, XK_F5, XK_F6,
        XK_F7, XK_F8, XK_F9, XK_F10, XK_F11, XK_F12,
        XK_KP_Equal, XK_KP_Subtract
    };
    printf("ok\n");
    return 0;
}
