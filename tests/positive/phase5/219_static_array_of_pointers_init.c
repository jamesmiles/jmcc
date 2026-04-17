// TEST: static_array_of_pointers_init
// DESCRIPTION: static pointer array initialized with static array names must resolve to their addresses
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* A static array of pointers whose initializers are names of other static
   arrays must be emitted with .quad symbol entries, not .quad 0.

       static int r1[] = {1, 2, 3};
       static int r2[] = {4, 5, 6};
       static int *im[] = { r1, r2 };   // im[0]==r1, im[1]==r2

   jmcc emits
       __static_main_im:
           .quad 0
           .quad 0
   so im[0] and im[1] are NULL at runtime. Dereferencing crashes.

   Reduced from rosettacode/reduced_row_echelon_form, which builds a matrix
   from three static row arrays via `static int *im[] = { r1, r2, r3 };` and
   SIGSEGVs because im[0] is NULL.

   Auto-storage (stack) array-of-pointers init works — the bug is specific
   to static-storage initialization emission. */

#include <stdio.h>

int main(void) {
    static int r1[] = {10, 20, 30};
    static int r2[] = {40, 50, 60};
    static int r3[] = {70, 80, 90};
    static int *im[] = { r1, r2, r3 };

    if (im[0] != r1) { printf("FAIL im[0]=%p r1=%p\n", (void*)im[0], (void*)r1); return 1; }
    if (im[1] != r2) { printf("FAIL im[1]=%p r2=%p\n", (void*)im[1], (void*)r2); return 2; }
    if (im[2] != r3) { printf("FAIL im[2]=%p r3=%p\n", (void*)im[2], (void*)r3); return 3; }

    if (im[0][0] != 10) return 4;
    if (im[1][2] != 60) return 5;
    if (im[2][1] != 80) return 6;

    /* Also covers file-scope, which Rosettacode also uses */
    printf("ok\n");
    return 0;
}
