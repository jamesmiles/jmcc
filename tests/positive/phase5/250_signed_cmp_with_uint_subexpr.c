// TEST: signed_cmp_with_uint_subexpr
// DESCRIPTION: signed i64 > with inline RHS containing 0xffffffff unsigned-int literal must use setg not seta
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c OP_DecrJumpZero (line ~100119):
     #define LARGEST_INT64  (0xffffffff|(((i64)0x7fffffff)<<32))
     #define SMALLEST_INT64 (((i64)-1) - LARGEST_INT64)
     if( pIn1->u.i > SMALLEST_INT64 ) pIn1->u.i--;
   Bug: 0xffffffff is an unsigned int literal.  When the full expression is
   evaluated inline (not through a typed i64 variable), jmcc infers the OR
   result as unsigned and emits `seta` (unsigned above) instead of `setg`
   (signed greater than) for the comparison.  For any positive i64 value,
   seta gives false (1 < 0x8000... unsigned) so LIMIT is never enforced.
   Fix: arithmetic between unsigned int and i64 must yield i64 (signed). */

#include <stdio.h>
typedef long long i64;

int main(void) {
    i64 x = 1;

    /* Inline form — must be true: 1 > INT64_MIN */
    if (!(x > ((i64)-1) - (0xffffffff|(((i64)0x7fffffff)<<32)))) {
        printf("FAIL: inline 1 > SMALLEST_INT64 should be true\n");
        return 1;
    }

    /* Simulate DecrJumpZero: counter starts at 1, should reach 0 */
    i64 counter = 1;
    if (counter > ((i64)-1) - (0xffffffff|(((i64)0x7fffffff)<<32))) counter--;
    if (counter != 0) {
        printf("FAIL: counter should be 0 after decrement, got %lld\n", counter);
        return 1;
    }

    printf("ok\n");
    return 0;
}
