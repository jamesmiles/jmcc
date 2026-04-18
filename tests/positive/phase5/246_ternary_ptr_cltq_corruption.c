// TEST: ternary_ptr_cltq_corruption
// DESCRIPTION: ternary where false-branch is address-of-local must not cltq-corrupt the 64-bit pointer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c line 112045:
     sqlite3FindInIndex(..., destIfFalse==destIfNull ? 0 : &rRhsHasNull, ...)
   Bug: jmcc emits `cltq` after the ternary to widen the result, but when
   the false-branch is `leaq addr(%rbp),%rax`, cltq sign-extends the low
   32 bits of the address, corrupting it (e.g. 0x7fffffffbca0 -> 0xffffffffffffbca0).
   Fix: don't emit cltq when the ternary result type is a pointer. */

#include <stdio.h>

int main(void) {
    int x = 0;
    int a = 1, b = 2;

    /* false branch: &x is a 64-bit pointer; cltq must not corrupt it */
    int *p = (a == b) ? 0 : &x;
    if (!p) { printf("FAIL: p is null (ternary chose wrong branch or corrupted ptr)\n"); return 1; }
    *p = 42;
    if (x != 42) { printf("FAIL: x=%d\n", x); return 1; }

    /* true branch: result should be null */
    int *q = (a == a) ? 0 : &x;
    if (q)  { printf("FAIL: q not null\n"); return 1; }

    printf("ok\n");
    return 0;
}
