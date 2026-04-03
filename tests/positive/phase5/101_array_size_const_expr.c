// TEST: array_size_const_expr
// DESCRIPTION: Array size with constant multiplication must allocate full size
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom has: int vol_lookup[128*256];  (32768 ints = 131072 bytes)
   The compiler allocates only 4 bytes (.zero 4) instead of 131072.
   The constant expression 128*256 in the array dimension is not
   being evaluated, so the array gets sizeof(int) * 1 instead of
   sizeof(int) * 32768.

   When I_UpdateSound writes to vol_lookup, it overwrites all globals
   after it in memory, causing widespread corruption. */

int printf(const char *fmt, ...);

int arr[16*4];     /* should be 64 ints = 256 bytes */
int sentinel = 99;

int main(void) {
    /* sizeof must report full size */
    if (sizeof(arr) != 16 * 4 * sizeof(int)) return 1;

    /* Write to last element */
    arr[63] = 42;
    if (arr[63] != 42) return 2;

    /* Sentinel should not be corrupted */
    if (sentinel != 99) return 3;

    printf("ok\n");
    return 0;
}
