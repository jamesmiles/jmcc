// TEST: parenthesized_declarator
// DESCRIPTION: declarators may be wrapped in redundant parentheses: `char *(arr[])`
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C grammar allows redundant parentheses around a declarator:
     T (name[])    is equivalent to   T name[]
     T *(name[])   is equivalent to   T *name[]
     T (*name)()   is REQUIRED (function pointer — different meaning than T *name())

   SQLite's shell.c uses this form in its help text table:
     static const char *(azHelp[]) = { ... };

   jmcc's parser rejects the redundant parenthesized form with
   "expected variable name, got '(' (LPAREN)". The parser must accept
   a parenthesized declarator as equivalent to the inner declarator. */

#include <stdio.h>

/* File-scope: this is the exact form shell.c uses */
static const char *(g_arr[]) = { "hello", "world" };

int (g_x) = 42;

int main(void) {
    if (g_arr[0][0] != 'h') return 100;
    if (g_arr[1][0] != 'w') return 101;
    if (g_x != 42) return 102;

    /* Parenthesized array declarator with pointer base type */
    static const char *(arr[]) = { "hello", "world" };
    if (arr[0][0] != 'h') return 1;
    if (arr[1][0] != 'w') return 2;

    /* Parenthesized with no base-type prefix */
    int (x) = 42;
    if (x != 42) return 3;

    /* Parenthesized array name */
    int (y[3]) = { 1, 2, 3 };
    if (y[0] + y[1] + y[2] != 6) return 4;

    /* Pointer + parens */
    int a = 99;
    int *(p) = &a;
    if (*p != 99) return 5;

    printf("ok\n");
    return 0;
}
