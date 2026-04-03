// TEST: 2d_int_array_stride
// DESCRIPTION: 2D array of ints must use correct stride for first dimension
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Test that non-struct 2D arrays also use the correct stride.
   For int arr[3][5], arr[1][0] should be at offset 5*4=20, not 4. */

int printf(const char *fmt, ...);

int grid[3][5];

int main(void) {
    int i, j;
    for (i = 0; i < 3; i++)
        for (j = 0; j < 5; j++)
            grid[i][j] = 0;

    grid[0][0] = 10;
    grid[1][0] = 20;
    grid[0][1] = 30;
    grid[2][4] = 99;

    if (grid[0][0] != 10) return 1;
    if (grid[1][0] != 20) return 2;
    if (grid[0][1] != 30) return 3;

    /* Make sure grid[1][0] didn't overwrite grid[0][1] */
    if (grid[0][1] != 30) return 4;
    /* Make sure grid[0][1] didn't overwrite grid[1][0] */
    if (grid[1][0] != 20) return 5;

    if (grid[2][4] != 99) return 6;

    printf("ok\n");
    return 0;
}
