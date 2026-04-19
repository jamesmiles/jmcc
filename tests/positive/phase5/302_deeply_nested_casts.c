// TEST: deeply_nested_casts
// DESCRIPTION: deeply nested cast expressions (35+ levels) must not cause Python RecursionError in parser
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
int main(void) {
    void *x = (void*)0;
    (void)((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(((int*)(x))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))));
    printf("OK\n");
    return 0;
}
