// TEST: alignof
// DESCRIPTION: _Alignof (C11) and __alignof__ (GCC) must work as alignment query operators
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

int main(void) {
    int a = _Alignof(double);
    int b = _Alignof(int);
    int c = __alignof__(char);
    if (a <= 0 || b <= 0 || c <= 0) return 1;
    if (a < b) return 2;  /* double alignment >= int alignment */
    printf("OK\n");
    return 0;
}
