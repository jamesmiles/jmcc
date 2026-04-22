/* Test: POSIX errno constants beyond EWOULDBLOCK.
 *
 * Reproduces the blocker in Chocolate Doom's m_misc.c, which checks
 * errno == EISDIR after a failed open()/mkdir() call.
 *
 * Root cause: jmcc's FALLBACK_HEADER for errno.h only defines
 * EWOULDBLOCK; common POSIX errno values (EISDIR, ENOENT, EEXIST, …)
 * are absent, so the preprocessor leaves them undefined.
 *
 * clang: OK
 * jmcc (arm64-apple-darwin): error: undefined variable 'EISDIR'
 */

#include <errno.h>

/* Check that a handful of common errno constants are visible */
int check_errno(int e) {
    if (e == ENOENT)  return 1;   /* No such file or directory */
    if (e == EEXIST)  return 2;   /* File exists */
    if (e == EISDIR)  return 3;   /* Is a directory */
    if (e == ENOTDIR) return 4;   /* Not a directory */
    if (e == EACCES)  return 5;   /* Permission denied */
    if (e == EINVAL)  return 6;   /* Invalid argument */
    if (e == ENOMEM)  return 7;   /* Out of memory */
    if (e == ERANGE)  return 8;   /* Result too large */
    if (e == EPERM)   return 9;   /* Operation not permitted */
    if (e == EIO)     return 10;  /* I/O error */
    return 0;
}

int main(void) {
    return check_errno(0);
}
