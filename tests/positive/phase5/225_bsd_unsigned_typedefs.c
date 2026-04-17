// TEST: bsd_unsigned_typedefs
// DESCRIPTION: BSD-style typedefs (uint, ushort, ulong, uchar) from sys/types.h must be available
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* glibc's sys/types.h (and BSD historically) defines short aliases:
       typedef unsigned int   uint;
       typedef unsigned short ushort;
       typedef unsigned long  ulong;
       typedef unsigned char  u_char;   // also u_int, u_short, u_long
   Many real-world programs use these without explicitly including
   <sys/types.h>, relying on transitive inclusion via other headers.

   jmcc's bundled headers don't provide them, so code like
     long ipow(int n, uint e) { ... }
   fails with "expected type specifier" at the `uint` token.

   Reduced from rosettacode/loops_with_multiple_ranges which uses `uint`
   as a function parameter type. */

/* NOTE: deliberately NO #include <sys/types.h> — the original Rosetta
   source doesn't include it, relying on implicit transitive inclusion
   via <stdlib.h> in the glibc toolchain. jmcc must emulate this so
   `uint` is available after the common header set. */
#include <stdlib.h>
#include <stdio.h>

long ipow(int n, uint e) {
    long pr = n;
    if (e == 0) return 1;
    for (uint i = 2; i <= e; ++i) pr *= n;
    return pr;
}

int main(void) {
    if (ipow(11, 5) != 161051) return 1;

    uint a = 42;
    ushort b = 7;
    ulong c = 100000;
    if (a + b + c != 100049) return 2;

    printf("ok\n");
    return 0;
}
