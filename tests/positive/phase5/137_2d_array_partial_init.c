// TEST: 2d_array_partial_init
// DESCRIPTION: Partial row initializer {0} in 2D array must zero-fill remaining elements
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's r_bsp.c has:
     int checkcoord[12][4] = {
         {3,0,2,1}, {3,0,2,0}, {3,1,2,0},
         {0},  // only 1 initializer for 4-element row
         ...
     };
   The {0} row must emit {0,0,0,0} (zero-fill remaining 3 elements).
   If only 1 zero is emitted, the next row's data slides into positions
   1-3, misaligning all subsequent rows and corrupting the lookup table.

   This causes R_CheckBBox to compute wrong bounding box corners,
   leading to invalid BSP traversal and crashes. */

int printf(const char *fmt, ...);

int table[4][3] = {
    {1, 2, 3},
    {0},         /* must be {0, 0, 0} */
    {4, 5, 6},
    {7, 8, 9}
};

int main(void) {
    /* Row 0: fully initialized */
    if (table[0][0] != 1) return 1;
    if (table[0][2] != 3) return 2;

    /* Row 1: partially initialized — remaining must be 0 */
    if (table[1][0] != 0) return 3;
    if (table[1][1] != 0) return 4;  /* FAILS if next row's data leaks in */
    if (table[1][2] != 0) return 5;

    /* Row 2: should be {4,5,6}, not shifted */
    if (table[2][0] != 4) return 6;
    if (table[2][1] != 5) return 7;
    if (table[2][2] != 6) return 8;

    /* Row 3 */
    if (table[3][0] != 7) return 9;
    if (table[3][2] != 9) return 10;

    printf("ok\n");
    return 0;
}
