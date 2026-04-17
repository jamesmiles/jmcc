// TEST: nested_function
// DESCRIPTION: GCC nested functions: a function definition inside another function body
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* GCC extension: nested functions. A function can be defined inside
   another function's body, with scope local to the enclosing function
   and access to the enclosing frame's variables.

       long outer(long x) {
           long inner(long n) { return n * 2; };
           return inner(x);
       }

   jmcc's parser rejects the inner definition with
   "expected ';', got '{'" at the inner function body's opening brace.

   Used by rosettacode/anonymous_recursion to define a recursive helper
   scoped to the outer function. Implementing requires trampoline codegen
   for the inner closure (executable stack / heap page). */

#include <stdio.h>

long outer(long x) {
    /* Basic case: no captured variables */
    long inner(long n) { return n * 2; };
    return inner(x);
}

long outer_rec(long x) {
    /* Self-recursive nested function */
    long fib(long n) { return n < 2 ? n : fib(n - 2) + fib(n - 1); };
    return fib(x);
}

int main(void) {
    if (outer(5) != 10) return 1;
    if (outer_rec(6) != 8) return 2;
    printf("ok\n");
    return 0;
}
