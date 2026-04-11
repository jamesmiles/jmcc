// TEST: shortpp_double_index
// DESCRIPTION: short** double indexing must work correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's r_data.c has: short** texturecolumnlump;
   Accessed as: lump = texturecolumnlump[tex][col];
   This is ptr_to_ptr[i][j] where the element type is short.
   The first index must stride by sizeof(short*) = 8,
   the second by sizeof(short) = 2. */

int printf(const char *fmt, ...);
void *malloc(long);

int main(void) {
    /* Create short** structure */
    short **table = (short **)malloc(3 * sizeof(short *));
    table[0] = (short *)malloc(4 * sizeof(short));
    table[1] = (short *)malloc(4 * sizeof(short));
    table[2] = (short *)malloc(4 * sizeof(short));

    table[0][0] = 100;
    table[0][3] = 400;
    table[1][0] = 500;
    table[1][2] = 700;
    table[2][1] = 800;

    /* Double indexing */
    if (table[0][0] != 100) return 1;
    if (table[0][3] != 400) return 2;
    if (table[1][0] != 500) return 3;
    if (table[1][2] != 700) return 4;
    if (table[2][1] != 800) return 5;

    /* Variable indices */
    int tex = 1;
    int col = 2;
    short val = table[tex][col];
    if (val != 700) return 6;

    /* unsigned short** pattern */
    unsigned short **utable = (unsigned short **)malloc(2 * sizeof(unsigned short *));
    utable[0] = (unsigned short *)malloc(4 * sizeof(unsigned short));
    utable[0][0] = 50000;
    utable[0][3] = 60000;

    if (utable[0][0] != 50000) return 7;
    if (utable[0][3] != 60000) return 8;

    printf("ok\n");
    return 0;
}
