// TEST: 2d_pointer_array_stride
// DESCRIPTION: 2D array of pointers must use correct stride for first dimension
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom declares: lighttable_t* scalelight[LIGHTLEVELS][MAXLIGHTSCALE]
   (16 x 48 array of pointers). When indexing scalelight[i][j], the
   first dimension stride should be MAXLIGHTSCALE * sizeof(pointer) = 48 * 8 = 384.

   If the compiler uses sizeof(pointer) = 8 as the stride for both dimensions,
   scalelight[1][0] points to offset 8 instead of offset 384, causing
   R_ExecuteSetViewSize to corrupt scalelight entries and crash the renderer. */

int printf(const char *fmt, ...);

char data[256];
char *table[4][8];

int main(void) {
    int i, j;

    /* Initialize all to NULL */
    for (i = 0; i < 4; i++)
        for (j = 0; j < 8; j++)
            table[i][j] = 0;

    /* Set table[0][0] and table[1][0] to different values */
    table[0][0] = &data[0];
    table[1][0] = &data[100];
    table[0][1] = &data[50];

    /* Verify table[0][0] wasn't corrupted by table[1][0] write */
    if (table[0][0] != &data[0]) return 1;

    /* Verify table[1][0] has correct value (stride bug would put it at wrong offset) */
    if (table[1][0] != &data[100]) return 2;

    /* Verify table[0][1] is correct */
    if (table[0][1] != &data[50]) return 3;

    /* Cross-verify: table[1][0] shouldn't overlap with table[0][1] */
    if (table[1][0] != &data[100]) return 4;
    if (table[0][1] != &data[50]) return 5;

    /* Test the Doom pattern: colormaps + level*256 stored in 2D ptr array */
    for (i = 0; i < 4; i++)
        for (j = 0; j < 8; j++)
            table[i][j] = data + (i * 8 + j);

    /* Verify all entries are correct */
    for (i = 0; i < 4; i++)
        for (j = 0; j < 8; j++)
            if (table[i][j] != data + (i * 8 + j))
                return 10 + i * 8 + j;

    printf("ok\n");
    return 0;
}
