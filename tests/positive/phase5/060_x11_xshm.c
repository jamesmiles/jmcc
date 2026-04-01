// TEST: x11_xshm
// DESCRIPTION: X11 shared memory extension types (Doom's i_video.c XShm usage)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/Xlib.h>
#include <X11/extensions/XShm.h>

int printf(const char *fmt, ...);

int main(void) {
    XShmSegmentInfo shminfo;
    shminfo.shmid = 0;
    shminfo.shmaddr = 0;
    shminfo.readOnly = 0;
    printf("ok\n");
    return 0;
}
