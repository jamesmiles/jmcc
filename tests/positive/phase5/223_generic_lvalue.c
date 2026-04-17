// TEST: generic_lvalue
// DESCRIPTION: _Generic result must preserve lvalue-ness of the selected branch
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C11 §6.5.1.1: "The type and value of a generic selection are identical
   to those of its result expression." That includes value category — so
   if the selected branch is an lvalue, the _Generic expression is an
   lvalue and can be assigned to.

       _Generic(x, int: x, default: x) = 42;   // valid

   jmcc rejects this with "expression is not an lvalue", so any code that
   uses _Generic as the left-hand side of an assignment fails to compile.

   Reduced from rosettacode/history_variables, whose `hv(V) = value` macro
   dispatches via _Generic to `*(T*)(V = ...)` and assigns through the
   pointer deref. */

#include <stdio.h>

int main(void) {
    int x = 0;
    _Generic(x, int: x, default: x) = 42;
    if (x != 42) return 1;

    /* Pointer dereference through _Generic — the real pattern used by
       history_variables.c */
    int a = 0, *p = &a;
    _Generic(*p, int: *p, default: *p) = 99;
    if (a != 99) return 2;

    /* Multiple types in the selector */
    double d = 0.0;
    _Generic(d,
        int: d,
        double: d,
        default: d) = 3.14;
    if (d != 3.14) return 3;

    printf("ok\n");
    return 0;
}
