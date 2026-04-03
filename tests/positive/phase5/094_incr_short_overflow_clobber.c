// TEST: incr_short_overflow_clobber
// DESCRIPTION: Increment/decrement on short member must not clobber adjacent field on overflow
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* The unary ++/-- code path uses movl for non-pointer types.
   Like compound assignments, this clobbers adjacent fields when
   the short wraps. Test 090 passed because it used non-overflowing
   values; this test triggers the overflow case. */

int printf(const char *fmt, ...);

struct pair {
    short lo;
    short hi;
};

int main(void) {
    struct pair p;

    /* Increment overflow: 0xFFFF + 1 = 0x10000, carry into hi */
    p.lo = -1;   /* 0xFFFF */
    p.hi = 0;
    p.lo++;

    if (p.lo != 0) return 1;
    if (p.hi != 0) return 2;   /* FAILS if carry clobbers hi */

    /* Decrement underflow: 0x0000 - 1 = 0xFFFF, borrow from hi */
    p.lo = 0;
    p.hi = 1;
    p.lo--;

    if (p.lo != -1) return 3;
    if (p.hi != 1) return 4;   /* FAILS if borrow clobbers hi */

    printf("ok\n");
    return 0;
}
