// TEST: fn_type_param_with_named_params
// DESCRIPTION: Function-type parameter with named sub-parameters must decay to pointer (used by CPython _heapqmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

static int apply(int arr[], int fn(int *, int), int n) {
    return fn(arr, n);
}

static int sum(int *a, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}

int main(void) {
    int a[] = {1, 2, 3};
    if (apply(a, sum, 3) != 6) return 1;
    printf("OK\n");
    return 0;
}
