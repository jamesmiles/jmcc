// TEST: array_typedef_indexing
// DESCRIPTION: Array-of-typedef-array: indexing must yield the typedef'd row, not a scalar
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When an array type is reached through a typedef, indexing the outer
   array must yield the row (which decays to a pointer), not a single
   element of the inner type.

       typedef unsigned char key_t[8];
       const key_t keys[] = { {0x13, ...}, {0x0E, ...} };
       keys[0]      // should be const unsigned char[8] (decays to const unsigned char*)
       keys[0][0]   // should be 0x13

   jmcc's type resolver unwraps the typedef too early, making `keys` look
   like a flat `unsigned char[N]`. Then `keys[0]` reads one byte (0x13)
   and returns it as a scalar. When passed to a function expecting a
   pointer, the byte value is interpreted as an address and crashes on
   the first dereference.

   Reduced from rosettacode/data_encryption_standard. With a bare 2D
   declaration `const unsigned char keys[][8]` it works. With the typedef
   form it crashes. */

#include <stdio.h>

typedef unsigned char ubyte;
typedef ubyte key_t[8];

static void take_ptr(const ubyte *p) {
    (void)p;
}

int main(void) {
    const key_t keys[] = {
        {0x13, 0x34, 0x57, 0x79, 0x9B, 0xBC, 0xDF, 0xF1},
        {0x0E, 0x32, 0x92, 0x32, 0xEA, 0x6D, 0x0D, 0x73},
    };

    /* keys[0] must be a pointer (const ubyte*), NOT a scalar byte */
    const ubyte *row0 = keys[0];
    const ubyte *row1 = keys[1];

    /* row0 and row1 must differ by 8 bytes (size of inner array) */
    if (row1 - row0 != 8) {
        printf("FAIL stride: row0=%p row1=%p diff=%ld (want 8)\n",
               (void*)row0, (void*)row1, (long)(row1 - row0));
        return 1;
    }

    /* Must read correct byte values through the row pointer */
    if (row0[0] != 0x13) { printf("FAIL row0[0]=0x%02x\n", row0[0]); return 2; }
    if (row1[0] != 0x0E) { printf("FAIL row1[0]=0x%02x\n", row1[0]); return 3; }
    if (row0[7] != 0xF1) { printf("FAIL row0[7]=0x%02x\n", row0[7]); return 4; }

    /* Passing to a function expecting a pointer must pass the address,
       not the first byte value (0x13 misinterpreted as a pointer crashes) */
    take_ptr(keys[0]);
    take_ptr(keys[1]);

    printf("ok\n");
    return 0;
}
