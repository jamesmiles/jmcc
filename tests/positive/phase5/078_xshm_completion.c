// TEST: xshm_completion
// DESCRIPTION: ShmCompletion constant from X11/extensions/XShm.h (Doom's i_video.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <X11/extensions/XShm.h>

int printf(const char *fmt, ...);

int main(void) {
    int event_type = ShmCompletion;
    printf("ok\n");
    return 0;
}
