// TEST: fnptr_returning_fnptr_cast
// DESCRIPTION: cast to function-pointer-returning-function-pointer type (inline, no typedef)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* jmcc can parse a simple function pointer cast:
       (void(*)(void))f
   but fails with "expected ')', got '('" on a cast where the return
   type of the function pointer is itself a spelled-out function pointer:
       (void(*(*)(void*,const char*))(void))f

   This is the exact cast in SQLite's unixDlSym (sqlite3.c):

       void (*(*x)(void*,const char*))(void);
       x = (void(*(*)(void*,const char*))(void))dlsym;

   The type reads (inside-out): pointer to a function(void*, const char*)
   that returns a pointer to a function(void) returning void.
   GCC accepts this; jmcc's parser chokes at the second '(' inside
   the outer parameter list of the cast type. */

#include <stdio.h>

/* Concrete helper that matches the inner signature void(*)(void) */
static void noop(void) {}

/* Returns a function pointer — matches void(*)(void*,const char*)'s return */
static void (*resolver(void *h, const char *sym))(void) {
    (void)h; (void)sym;
    return noop;
}

int main(void) {
    /* Declare a variable of the complex type */
    void (*(*x)(void*, const char*))(void);

    /* Cast resolver to the same type — this is the pattern jmcc fails on */
    x = (void(*(*)(void*, const char*))(void))resolver;

    /* Call through the double function pointer */
    void (*fn)(void) = x(0, "noop");
    if (fn == 0) { printf("FAIL fn is null\n"); return 1; }
    fn();  /* must not crash */

    /* Also test the simpler nested case: pointer-to-fn returning pointer */
    void *(*y)(void*, const char*);
    y = (void*(*)(void*, const char*))resolver;
    if (y == 0) { printf("FAIL y is null\n"); return 2; }

    printf("ok\n");
    return 0;
}
