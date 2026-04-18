// TEST: int128_basic
// DESCRIPTION: __int128 type: declaration, sizeof, assignment, cast to/from smaller types
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Foundational __int128 support: the type must be parseable, have
   sizeof 16, be assignable from integer literals and smaller types,
   and be castable back to smaller integer types. No arithmetic yet. */

#include <stdio.h>

int main(void) {
    __int128 a = 0;
    __int128 b = 1;
    __int128 c = -1;
    __int128 d = 42;
    unsigned __int128 u = 0;

    if (sizeof(__int128) != 16) {
        printf("FAIL sizeof: %zu\n", sizeof(__int128));
        return 1;
    }
    if ((int)a != 0)  { printf("FAIL a=%d\n", (int)a);  return 2; }
    if ((int)b != 1)  { printf("FAIL b=%d\n", (int)b);  return 3; }
    if ((int)c != -1) { printf("FAIL c=%d\n", (int)c);  return 4; }
    if ((int)d != 42) { printf("FAIL d=%d\n", (int)d);  return 5; }

    /* assign from long long */
    __int128 e = (long long)0x7FFFFFFFFFFFFFFFLL;
    if ((long long)e != 0x7FFFFFFFFFFFFFFFLL) {
        printf("FAIL e\n"); return 6;
    }

    /* assign from unsigned long long */
    __int128 f = (unsigned long long)0xFFFFFFFFFFFFFFFFULL;
    if ((unsigned long long)f != 0xFFFFFFFFFFFFFFFFULL) {
        printf("FAIL f\n"); return 7;
    }

    (void)u;
    printf("ok\n");
    return 0;
}
