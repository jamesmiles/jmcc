// TEST: include_sys_ipc_shm
// DESCRIPTION: SysV IPC/shared memory types (Doom's i_video.c shmget/shmctl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/ipc.h>
#include <sys/shm.h>

int printf(const char *fmt, ...);

int main(void) {
    key_t key = 0;
    int shmid = 0;
    struct shmid_ds shminfo;
    printf("ok\n");
    return 0;
}
