// TEST: block_ptr_syntax
// DESCRIPTION: Darwin stdlib.h declares functions that take Apple C Blocks (^) as
//              parameters, e.g. int atexit_b(void (^ _Nonnull)(void));
//              jmcc must be able to parse these block pointer declarations without
//              aborting, even if it does not generate code for block calls.
//              Regression test for Chocolate Doom / stdlib.h include chain on arm64.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef void (^void_block)(void);
typedef int  (^compare_block)(const void *, const void *);

int main(void) {
    printf("OK\n");
    return 0;
}
