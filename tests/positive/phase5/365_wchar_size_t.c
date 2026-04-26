// TEST: wchar_size_t
// DESCRIPTION: wchar.h must provide size_t (CPython pyport.h uses size_t after #include <wchar.h> without stdlib.h)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <wchar.h>
/* size_t must come from wchar.h — no other headers above this line */
typedef size_t my_size;
#include <stdio.h>

int main(void) {
    my_size n = sizeof(int);
    if (n == 0) return 1;
    printf("OK\n");
    return 0;
}
