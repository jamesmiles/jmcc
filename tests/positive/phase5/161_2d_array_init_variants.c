// TEST: 2d_array_init_variants
// DESCRIPTION: Various 2D array initialization patterns must produce correct data
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Cover 2D array init patterns not yet tested:
   braced rows, flat init, fewer rows, local arrays,
   char-by-char init. */

int printf(const char *fmt, ...);

/* Braced row initializers */
int grid[2][3] = {{10, 20, 30}, {40, 50, 60}};

/* Flat initializer (no inner braces) */
int flat[2][3] = {1, 2, 3, 4, 5, 6};

/* Fewer rows than declared — remaining rows should be zero */
int sparse[3][2] = {{7, 8}, {9, 10}};

/* Char-by-char (not string literal) */
char chars[2][3] = {{'X', 'Y', 'Z'}, {'A', 'B', 'C'}};

int main(void) {
    /* Test 1: braced row init */
    if (grid[0][0] != 10) return 1;
    if (grid[0][2] != 30) return 2;
    if (grid[1][0] != 40) return 3;
    if (grid[1][2] != 60) return 4;

    /* Test 2: flat init */
    if (flat[0][0] != 1) return 10;
    if (flat[0][2] != 3) return 11;
    if (flat[1][0] != 4) return 12;
    if (flat[1][2] != 6) return 13;

    /* Test 3: sparse — third row should be all zeros */
    if (sparse[0][0] != 7) return 20;
    if (sparse[1][1] != 10) return 21;
    if (sparse[2][0] != 0) return 22;
    if (sparse[2][1] != 0) return 23;

    /* Test 4: char-by-char init */
    if (chars[0][0] != 'X') return 30;
    if (chars[0][2] != 'Z') return 31;
    if (chars[1][0] != 'A') return 32;
    if (chars[1][2] != 'C') return 33;

    /* Test 5: local 2D array init */
    int local[2][2] = {{100, 200}, {300, 400}};
    if (local[0][0] != 100) return 40;
    if (local[1][1] != 400) return 41;

    /* Test 6: local 2D char array with strings */
    char lnames[2][5] = {"one", "two"};
    if (lnames[0][0] != 'o') return 50;
    if (lnames[0][2] != 'e') return 51;
    if (lnames[1][0] != 't') return 52;
    if (lnames[1][2] != 'o') return 53;

    printf("ok\n");
    return 0;
}
