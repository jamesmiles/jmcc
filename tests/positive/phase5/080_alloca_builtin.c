// TEST: alloca_builtin
// DESCRIPTION: alloca() stack allocation used by Doom (10 files, linker error)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: A
// STDOUT: Z
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom uses alloca() in 10 files for temporary stack allocations.
   On Linux, alloca is a compiler builtin that adjusts %rsp inline.
   JMCC emits a regular call to alloca() which doesn't exist as a
   library function, causing "undefined reference to alloca" at link time.

   JMCC needs either:
   1. A builtin alloca that emits inline stack adjustment, or
   2. A stub alloca implementation linked in */

#include <alloca.h>

int printf(const char *fmt, ...);

int main(void) {
    int size = 100;
    char *buf = (char *)alloca(size);
    buf[0] = 'A';
    buf[99] = 'Z';
    printf("%c\n", buf[0]);
    printf("%c\n", buf[99]);
    return 0;
}
