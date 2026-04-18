// TEST: i64_signed_gt_int64min
// DESCRIPTION: signed 64-bit greater-than comparison against INT64_MIN must use setg not seta
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c OP_DecrJumpZero (line 100119):
     if( pIn1->u.i > SMALLEST_INT64 ) pIn1->u.i--;
     if( pIn1->u.i==0 ) goto jump_to_p2;
   SMALLEST_INT64 = INT64_MIN = 0x8000000000000000.
   Bug: jmcc emits `seta` (unsigned "above") instead of `setg` (signed "greater
   than") for the i64 > SMALLEST_INT64 comparison.  For any positive LIMIT value
   (e.g. 1), seta gives false (1 < 0x8000... unsigned) so the counter is never
   decremented, never reaches 0, and LIMIT is never enforced — all rows returned.
   Fix: use setg (or equivalent signed branch) for signed 64-bit comparisons. */

#include <stdio.h>

int main(void) {
    long long x = 1LL;
    /* INT64_MIN: can't write -9223372036854775808 directly as a signed literal */
    long long smallest = -9223372036854775807LL - 1LL;

    /* 1 > INT64_MIN is true for signed comparison */
    if (!(x > smallest)) {
        printf("FAIL: 1 > INT64_MIN should be true (signed)\n");
        return 1;
    }

    /* INT64_MIN > INT64_MIN is false */
    if (smallest > smallest) {
        printf("FAIL: INT64_MIN > INT64_MIN should be false\n");
        return 1;
    }

    /* -1 > INT64_MIN is true */
    long long neg1 = -1LL;
    if (!(neg1 > smallest)) {
        printf("FAIL: -1 > INT64_MIN should be true\n");
        return 1;
    }

    /* simulate the DecrJumpZero pattern: decrement while > SMALLEST_INT64 */
    long long counter = 2LL;
    if (counter > smallest) counter--;
    if (counter != 1LL) {
        printf("FAIL: counter should be 1 after decrement, got %lld\n", counter);
        return 1;
    }
    if (counter > smallest) counter--;
    if (counter != 0LL) {
        printf("FAIL: counter should be 0 after decrement, got %lld\n", counter);
        return 1;
    }

    printf("ok\n");
    return 0;
}
