// TEST: vla_2d_stride
// DESCRIPTION: 2D VLA indexing must use row_size*elem_size for outer dim, not elem_size
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* A 2D VLA like `uint64_t arr[9][n]` (where n is a run-time value) must
   index with the correct stride per dimension:

       arr[i][j]  =  *(base + i * (n * sizeof(uint64_t)) + j * sizeof(uint64_t))

   jmcc emits the outer stride as plain `sizeof(uint64_t)` instead of
   `n * sizeof(uint64_t)`, so every write to arr[i][j] with i>0 lands at
   wrong offsets and writes to arr[0][k] with k>0 overwrite arr[1][k-1]
   etc. Later reads produce the corrupted values.

   Reduced from rosettacode/palindromic_gapful_numbers, which uses
   `integer pg1[9][n1]` with n1=20 and writes `pg1[digit-1][i] = n`,
   overwriting neighbouring rows and eventually the loop control variable,
   so the enclosing `for(i=0;i<1000;)` never terminates normally and
   crashes. Fixed-size 2D arrays are compiled correctly — the bug is
   VLA-specific. */

#include <stdio.h>
#include <stdint.h>

int main(void) {
    int n = 3;  /* makes arr a VLA */
    uint64_t arr[2][n];

    arr[0][0] = 10; arr[0][1] = 11; arr[0][2] = 12;
    arr[1][0] = 20; arr[1][1] = 21; arr[1][2] = 22;

    if (arr[0][0] != 10) return 1;
    if (arr[0][1] != 11) return 2;
    if (arr[0][2] != 12) return 3;
    if (arr[1][0] != 20) return 4;
    if (arr[1][1] != 21) return 5;
    if (arr[1][2] != 22) return 6;

    /* Pointer arithmetic on the row must also use the correct stride */
    uint64_t (*prow)[3] = (uint64_t (*)[3])arr;
    if (prow[0][0] != 10 || prow[1][2] != 22) return 7;

    /* Larger VLA, typical pattern: [outer][vla_inner] */
    int m = 20;
    uint64_t big[9][m];
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < m; c++)
            big[r][c] = (uint64_t)r * 1000 + c;
    int ok = 1;
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < m; c++)
            if (big[r][c] != (uint64_t)r * 1000 + c) ok = 0;
    if (!ok) return 8;

    printf("ok\n");
    return 0;
}
