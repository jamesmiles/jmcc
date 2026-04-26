// TEST: ptr_to_array_param
// DESCRIPTION: function parameter of type pointer-to-array "int (*arr)[5]" must parse (C standard type)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

void process(int (*arr)[5]) {
    (*arr)[0] = 42;
}

int main(void) {
    int a[5] = {0};
    process(&a);
    printf("%d\n", a[0]);
    printf("OK\n");
    return 0;
}
