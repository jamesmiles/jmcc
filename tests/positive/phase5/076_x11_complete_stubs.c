// TEST: x11_complete_stubs
// DESCRIPTION: All X11 types, struct members, and constants needed by Doom's i_video.c
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <X11/extensions/XShm.h>
#include <sys/ipc.h>
#include <sys/shm.h>

int printf(const char *fmt, ...);

int main(void) {
    /* === Types === */
    Display *dpy;
    Window win;
    Visual *vis;
    Colormap cmap;
    GC gc;
    Cursor cursor;
    Pixmap pixmap;
    KeySym key;
    Atom atom;

    /* === XEvent union and sub-struct members === */
    XEvent event;
    int t = event.type;
    unsigned int kc = event.xkey.keycode;
    unsigned int bs = event.xbutton.state;
    unsigned int bb = event.xbutton.button;
    unsigned int ms = event.xmotion.state;
    int mx = event.xmotion.x;
    int my = event.xmotion.y;
    int ec = event.xexpose.count;

    /* === XSetWindowAttributes members === */
    XSetWindowAttributes attribs;
    attribs.border_pixel = 0;
    attribs.colormap = 0;
    attribs.event_mask = 0;

    /* === XVisualInfo members === */
    XVisualInfo vinfo;
    vinfo.visual = 0;
    vinfo.depth = 8;
    /* vinfo.class is a keyword in C++ but valid in C */

    /* === XGCValues members === */
    XGCValues xgc;
    xgc.function = 0;

    /* === XImage members === */
    XImage *image;
    image = 0;
    /* image->data, image->bytes_per_line, image->height */

    /* === XShmSegmentInfo members === */
    XShmSegmentInfo shminfo_x;
    shminfo_x.shmid = 0;
    shminfo_x.shmaddr = 0;
    shminfo_x.readOnly = 0;

    /* === struct shmid_ds members === */
    struct shmid_ds shmds;
    int nattch = shmds.shm_nattch;
    int cpid = shmds.shm_cpid;
    int segsz = shmds.shm_segsz;
    int cuid = shmds.shm_perm.cuid;

    /* === Constants === */
    int c1 = PseudoColor;
    int c2 = DoRed | DoGreen | DoBlue;
    int c3 = GXclear;
    int c4 = None;
    int c5 = ZPixmap;
    int c6 = AllocAll;
    int c7 = InputOutput;
    int c8 = GrabModeAsync;
    unsigned long c9 = CurrentTime;
    long c10 = CWBorderPixel | CWColormap | CWEventMask;
    long c11 = GCFunction | GCGraphicsExposures;
    int c12 = KeyPress;
    int c13 = KeyRelease;
    int c14 = ButtonPress;
    int c15 = ButtonRelease;
    int c16 = MotionNotify;
    int c17 = Expose;
    long c18 = KeyPressMask | ExposureMask | ButtonPressMask | ButtonReleaseMask | PointerMotionMask;
    int c19 = Button1;
    int c20 = Button2;
    int c21 = Button3;
    unsigned int c22 = Button1Mask | Button2Mask | Button3Mask;
    int c23 = IPC_CREAT;
    int c24 = IPC_STAT;
    int c25 = IPC_PRIVATE;

    /* === Keysyms (sample) === */
    int k1 = XK_space;
    int k2 = XK_Return;
    int k3 = XK_Escape;
    int k4 = XK_Left;
    int k5 = XK_F1;

    printf("ok\n");
    return 0;
}
