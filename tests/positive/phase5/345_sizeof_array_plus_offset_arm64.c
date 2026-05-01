// TEST: sizeof_array_plus_offset_arm64
// DESCRIPTION: sizeof((arr + offset)[0]) — array+integer must decay to pointer
// in get_expr_type so element type can be resolved. Repro from Lua 5.4 ldump.c
// dumpSize macro: sizeof((buff + N - n)[0]).
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1 4 8
// PHASE: 5

#include <stdio.h>

int main(void) {
    unsigned char buff[16];
    int ints[8];
    long longs[4];
    int n = 2;
    /* Each printout is sizeof of (array + offset)[0], which is the element size. */
    printf("%zu %zu %zu\n",
           sizeof((buff + n)[0]),
           sizeof((ints + n)[0]),
           sizeof((longs + n)[0]));
    return 0;
}
