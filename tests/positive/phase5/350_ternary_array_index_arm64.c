// TEST: ternary_array_index_arm64
// DESCRIPTION: Indexing a ternary that yields an array — (cond ? a : b)[i].
// Repro from SQLite btree.c balance_nonroot:
//   MemPage *pOld = (nNew>nOld ? apNew : apOld)[nOld-1];
// arm64 gen_array_addr was calling gen_lvalue_addr on the ternary, which
// is not an lvalue and errored out.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 30 200
// PHASE: 5

#include <stdio.h>

int main(void) {
    int a[3] = {10, 20, 30};
    int b[3] = {100, 200, 300};
    int cond = 1;
    int notcond = 0;
    int x = (cond ? a : b)[2];
    int y = (notcond ? a : b)[1];
    printf("%d %d\n", x, y);
    return 0;
}
