// TEST: func_predefined
// DESCRIPTION: __func__ predefined identifier (C99) must be available inside functions as a string containing the function name
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <string.h>

static const char *get_name(void) {
    return __func__;
}

int main(void) {
    const char *n = get_name();
    if (strcmp(n, "get_name") != 0) return 1;
    if (strcmp(__func__, "main") != 0) return 2;
    printf("OK\n");
    return 0;
}
