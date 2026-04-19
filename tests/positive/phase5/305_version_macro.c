// TEST: version_macro
// DESCRIPTION: __VERSION__ predefined macro must be defined (string containing compiler version, used for string concatenation)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

/* __VERSION__ is a predefined GCC macro expanding to a string like "13.3.0"
   CPython's getcompiler.c uses: "[GCC " __VERSION__ "]" */
const char *compiler = "[jmcc " __VERSION__ "]";

int main(void) {
    if (compiler[0] != '[') return 1;
    printf("OK\n");
    return 0;
}
