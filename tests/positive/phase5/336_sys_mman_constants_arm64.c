/* Regression: jmcc's fallback sys/mman.h for arm64-apple-darwin does not
 * define the standard POSIX mmap constants: PROT_READ, PROT_WRITE,
 * MAP_PRIVATE, MAP_SHARED, MAP_ANON, etc.
 *
 * This blocks compilation of Chocolate Doom's w_file_posix.c which uses
 * mmap(NULL, len, PROT_READ|PROT_WRITE, MAP_PRIVATE, fd, 0) to map WAD
 * files into memory.
 *
 * clang resolves these from the real system <sys/mman.h>; jmcc's fallback
 * header must also define them.
 */
#include <sys/mman.h>

int main(void) {
    /* Verify the constants are defined and have sensible values */
    int prot  = PROT_READ | PROT_WRITE;
    int flags = MAP_PRIVATE;
    return (prot > 0 && flags > 0) ? 0 : 1;
}
