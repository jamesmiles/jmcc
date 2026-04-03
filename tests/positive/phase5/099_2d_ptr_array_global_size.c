// TEST: 2d_ptr_array_global_size
// DESCRIPTION: Global 2D pointer array must allocate full size (rows * cols * sizeof(ptr))
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom has global 2D pointer arrays like:
     lighttable_t* scalelight[16][48];   // should be 6144 bytes
     lighttable_t* zlight[16][128];      // should be 16384 bytes
   The compiler allocates only 8 bytes (.zero 8) instead of the full
   N*M*sizeof(pointer) size.

   Use sizeof to verify the array has the correct size. */

int printf(const char *fmt, ...);

char *table[4][8];   /* should be 4*8*8 = 256 bytes */

int main(void) {
    /* sizeof must report the full array size */
    if (sizeof(table) != 4 * 8 * sizeof(char *)) return 1;

    /* Write to the last element — this should NOT corrupt anything
       even though it's at byte offset (4*8-1)*8 = 248 from table start */
    table[3][7] = (char *)0xDEAD;

    /* Also verify first and last row starts are at expected offsets.
       Taking addresses: &table[1][0] - &table[0][0] should be 8 pointers apart */
    long diff = (char *)&table[1][0] - (char *)&table[0][0];
    if (diff != 8 * sizeof(char *)) return 2;  /* should be 64 bytes */

    /* Verify the write worked */
    if (table[3][7] != (char *)0xDEAD) return 3;

    printf("ok\n");
    return 0;
}
