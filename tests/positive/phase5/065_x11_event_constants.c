// TEST: x11_event_constants
// DESCRIPTION: X11 event/mask/mode constants needed by Doom's i_video.c
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>

int printf(const char *fmt, ...);

int main(void) {
    /* Event types */
    int a = KeyPress;
    int b = KeyRelease;
    int c = ButtonPress;
    int d = ButtonRelease;
    int e = MotionNotify;
    int f = Expose;

    /* Event masks */
    long m1 = KeyPressMask;
    long m2 = ExposureMask;
    long m3 = ButtonPressMask;
    long m4 = ButtonReleaseMask;
    long m5 = PointerMotionMask;

    /* Button constants */
    int b1 = Button1;
    int b2 = Button2;
    int b3 = Button3;
    unsigned int bm1 = Button1Mask;
    unsigned int bm2 = Button2Mask;
    unsigned int bm3 = Button3Mask;

    /* Window attributes */
    long cw1 = CWBorderPixel;
    long cw2 = CWColormap;
    long cw3 = CWEventMask;

    /* Misc */
    int io = InputOutput;
    int gc = GCGraphicsExposures;
    int aa = AllocAll;
    int zp = ZPixmap;
    int gm = GrabModeAsync;
    unsigned long ct = CurrentTime;

    /* IPC */
    int ic = IPC_CREAT;
    int is = IPC_STAT;

    printf("ok\n");
    return 0;
}
