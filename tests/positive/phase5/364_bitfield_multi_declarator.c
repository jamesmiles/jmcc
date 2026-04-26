// TEST: bitfield_multi_declarator
// DESCRIPTION: multiple bitfield declarators in one declaration: "int A:1, B:2, C:3;" must parse (CPython _ctypes_test.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef struct {
    signed int A: 1, B:2, C:3, D:2;
} S;

int main(void) {
    S s = {0, 1, 2, 1};
    if (s.B != 1 || s.C != 2) return 1;
    printf("OK\n");
    return 0;
}
