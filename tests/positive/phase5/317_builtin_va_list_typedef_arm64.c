// TEST: builtin_va_list_typedef
// DESCRIPTION: Darwin system headers typedef __builtin_va_list as __darwin_va_list.
//              jmcc must recognise __builtin_va_list as a valid type specifier so
//              that any header chain pulling in <stdarg.h>/<string.h> can be parsed.
//              Regression test for Chocolate Doom / am_map.c include chain.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef __builtin_va_list my_va_list;

int main(void) {
    printf("OK\n");
    return 0;
}
