// Test: sizeof(*ptr_array) where ptr_array element type is pointer
// arrlen macro in Chocolate Doom: sizeof(array)/sizeof(*array)
// When array is int*[], *array has type int* so sizeof(*array) should be 8 on arm64.
// jmcc bug: sizeof(*weapon_keys) returns 4 (sizeof int) instead of 8 (sizeof int*),
// causing arrlen(weapon_keys) = 64/4 = 16 instead of 8, loop overruns → null deref crash.
// Expected output: 8\n3\n
// exit: 0

#include <stdio.h>

#define arrlen(array) (sizeof(array) / sizeof(*array))

static int val_a = 1, val_b = 2, val_c = 3;
static int *ptrs[] = {&val_a, &val_b, &val_c};

int main(void) {
    int sz = (int)sizeof(*ptrs);
    int n  = (int)arrlen(ptrs);
    printf("%d\n", sz);  /* expected 8 */
    printf("%d\n", n);   /* expected 3 */
    return (sz == 8 && n == 3) ? 0 : 1;
}
