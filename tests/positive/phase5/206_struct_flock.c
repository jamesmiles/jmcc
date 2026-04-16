// TEST: struct_flock
// DESCRIPTION: fcntl.h must provide struct flock for POSIX file locking
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's unix VFS uses struct flock for POSIX file locking:
     struct flock lock;
     lock.l_whence = SEEK_SET;
     lock.l_type = F_RDLCK;
     fcntl(fd, F_SETLK, &lock);

   jmcc's built-in fcntl.h doesn't define struct flock, so SQLite
   can't compile its unix file locking code. */

#include <fcntl.h>

int printf(const char *fmt, ...);

int main(void) {
    struct flock lock;
    lock.l_type = F_RDLCK;
    lock.l_whence = 0;
    lock.l_start = 0;
    lock.l_len = 0;

    if (lock.l_type != F_RDLCK) return 1;
    if (lock.l_whence != 0) return 2;

    printf("ok\n");
    return 0;
}
