// TEST: stdbool_defined_macro
// DESCRIPTION: stdbool.h must define __bool_true_false_are_defined
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* The C99 standard requires stdbool.h to define the macro
   __bool_true_false_are_defined to 1. Chocolate Doom's doomtype.h
   checks this to decide between typedef int boolean (C99 path)
   and enum { false, true } boolean (pre-C99 path). Without this
   macro, stdbool.h's #define false 0 / #define true 1 corrupts
   the enum definition into enum { 0, 1 } which is invalid C. */

#include <stdbool.h>

int printf(const char *fmt, ...);

int main(void) {
#ifdef __bool_true_false_are_defined
    printf("ok\n");
    return 0;
#else
    return 1;
#endif
}
