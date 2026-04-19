// TEST: sys_stat_posix_typedefs
// DESCRIPTION: sys/stat.h must define dev_t, ino_t, mode_t typedefs (not just struct stat)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <sys/stat.h>

/* These types should be defined by sys/stat.h (used in CPython pycore_pyhash.h) */
struct my_stat_cache {
    int fd;
    dev_t st_dev;
    ino_t st_ino;
    mode_t st_mode;
};

int main(void) {
    struct my_stat_cache c;
    c.fd = -1;
    c.st_dev = 0;
    c.st_ino = 0;
    c.st_mode = 0;
    (void)c;
    printf("OK\n");
    return 0;
}
