// TEST: shm_perm
// DESCRIPTION: struct shmid_ds.shm_perm.cuid member (Doom's i_video.c shared memory)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/ipc.h>
#include <sys/shm.h>

int printf(const char *fmt, ...);

int main(void) {
    struct shmid_ds shminfo;
    int uid = shminfo.shm_perm.cuid;
    printf("ok\n");
    return 0;
}
