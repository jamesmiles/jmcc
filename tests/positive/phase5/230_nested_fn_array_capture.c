// TEST: nested_fn_array_capture
// DESCRIPTION: GCC nested function capturing a local array (decay vs pointer-to-array)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When a nested function captures a local array, the closure must store
   a pointer-to-array (T (*)[N]) rather than a plain pointer (T *).
   These are the same bit-representation but differ in type, which affects
   how jmcc emits the capture struct field and how the nested function
   dereferences it.

   A plain T * capture would work for single-dimensional indexing but
   silently produces wrong code if the captured variable's address is
   later taken or passed as T (*)[N].

   `_lift_nested_functions` must detect that the captured variable is an
   array type and emit the field as a pointer-to-array rather than a
   pointer-to-element. */

#include <stdio.h>

int sum_array(void) {
    int arr[4] = {10, 20, 30, 40};
    int total(void) {
        int s = 0, i;
        for (i = 0; i < 4; i++) s += arr[i];
        return s;
    }
    return total();
}

/* Also: modify an array element via the nested closure */
void fill_array(void) {
    int buf[3] = {0, 0, 0};
    void set(int idx, int val) { buf[idx] = val; }
    set(0, 7);
    set(1, 8);
    set(2, 9);
    if (buf[0] != 7 || buf[1] != 8 || buf[2] != 9) {
        printf("FAIL fill\n");
    }
}

int main(void) {
    if (sum_array() != 100) { printf("FAIL sum: got %d\n", sum_array()); return 1; }
    fill_array();
    printf("ok\n");
    return 0;
}
