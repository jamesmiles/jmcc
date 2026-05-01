// TEST: sys_types_off_t
// DESCRIPTION: <sys/types.h> must provide off_t (and friends) so a declaration
// like "off_t offset = (off_t)x;" parses. Repro from Lua liolib.c f_seek.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 8 8 4 0
// PHASE: 5

#include <stdio.h>
#include <sys/types.h>

int main(void) {
    off_t offset = (off_t)1234567890123LL;
    ssize_t s = (ssize_t)-1;
    pid_t p = 0;
    mode_t m = 0644;
    (void)offset; (void)s; (void)p; (void)m;
    /* Sizes: off_t=8, ssize_t=8, pid_t=4, plus a final 0 sentinel. */
    printf("%zu %zu %zu %d\n",
           sizeof(off_t), sizeof(ssize_t), sizeof(pid_t), 0);
    return 0;
}
