// TEST: system_struct_stat
// DESCRIPTION: struct stat with st_size member (Doom's w_wad.c file size check)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: size=1024
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom's w_wad.c uses fstat() and accesses buf.st_size.
   This requires <sys/stat.h> which defines struct stat.
   Test the pattern with a local struct definition. */
typedef long off_t;

struct stat {
    int st_dev;
    int st_ino;
    int st_mode;
    int st_nlink;
    int st_uid;
    int st_gid;
    int st_rdev;
    off_t st_size;
};

int main(void) {
    struct stat buf;
    buf.st_size = 1024;
    printf("size=%ld\n", buf.st_size);
    return 0;
}
