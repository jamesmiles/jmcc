// TEST: 2d_array_init_size
// DESCRIPTION: Initialized 2D array must emit all inner dimension data
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom has: byte gammatable[5][256] = { {0,0,0,...}, {0,0,0,...}, ... };
   The compiler emits only 5 bytes instead of 5*256=1280 bytes.
   The inner dimension data is truncated, so gammatable[1][0] through
   gammatable[4][255] all point to uninitialized/wrong memory.

   UploadNewPalette reads gammatable[usegamma][i] for i=0..255,
   crashing when the lookup goes beyond the allocated 5 bytes. */

int printf(const char *fmt, ...);

int table[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

int main(void) {
    /* sizeof must be correct */
    if (sizeof(table) != 3 * 4 * sizeof(int)) return 1;

    /* All values must be accessible */
    if (table[0][0] != 1) return 2;
    if (table[0][3] != 4) return 3;
    if (table[1][0] != 5) return 4;
    if (table[1][3] != 8) return 5;
    if (table[2][0] != 9) return 6;
    if (table[2][3] != 12) return 7;

    /* Byte array version (like gammatable) */
    /* Cannot test byte array directly without char init, but
       the int test covers the same codegen path */

    printf("ok\n");
    return 0;
}
