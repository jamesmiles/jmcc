// TEST: include_sys_stat
// DESCRIPTION: #include <sys/stat.h> for struct stat/st_size (Doom's w_wad.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <sys/stat.h>

int printf(const char *fmt, ...);

int main(void) {
    struct stat buf;
    buf.st_size = 1024;
    printf("ok\n");
    return 0;
}
