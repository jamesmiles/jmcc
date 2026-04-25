// TEST: attribute_on_typedef_fn
// DESCRIPTION: __attribute__ after function typedef declarator must be accepted (used by CPython readline.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef int Function() __attribute__((deprecated));
typedef void VFunction() __attribute__((deprecated));

int main(void) {
    printf("OK\n");
    return 0;
}
