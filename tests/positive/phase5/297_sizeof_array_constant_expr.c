// TEST: sizeof_array_constant_expr
// DESCRIPTION: sizeof(char[constant_expr]) compile-time assertion pattern must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

/* Compile-time assertion via sizeof(char[1 - 2*!(cond)]) */
#define STATIC_ASSERT(cond) \
    do { (void)(sizeof(char[1 - 2*!(cond)]) - 1); } while(0)

int main(void) {
    unsigned int x = 5;
    STATIC_ASSERT(sizeof(x) <= sizeof(unsigned int));
    STATIC_ASSERT(sizeof(x) == 4);
    printf("OK\n");
    return 0;
}
