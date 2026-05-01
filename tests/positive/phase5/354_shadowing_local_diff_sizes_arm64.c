// TEST: shadowing_local_diff_sizes_arm64
// DESCRIPTION: Two variables with the same name in mutually-exclusive scopes
// (here, opposite branches of an if/else) but DIFFERENT sizes — `double rr`
// in the if-branch vs `double rr[2]` in the else-branch — must each get a
// slot large enough for their own type. Previously alloc_slot() returned
// early on the second decl, leaving the array decl with only 8 bytes; writes
// to rr[1] then clobbered the next stack slot.
// Repro: SQLite's sqlite3FpDecode (lib/sqlite3.c). Compiling SELECT 1.5;
// produced "1.5e+g70" because the inner FpDecode loop's `exp -= 10;` was
// being clobbered by a subsequent f(rr,...) call writing past rr's slot.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -10 -20 -30
// PHASE: 5

#include <stdio.h>

static int dummy = 0;

static void f2(volatile double *x, double y, double yy) {
    volatile double tx, ty;
    double hx, hy;
    hx = y; hy = y;
    tx = x[0]; ty = y;
    x[0] = hx + hy + tx + ty + yy;
    x[1] = hx;   /* writes 8 bytes into rr[1] — needs full 16-byte slot */
}

static int run(double r) {
    int exp = 0;
    if (dummy) {
        double rr = r;          /* same name, scalar */
        (void)rr;
    } else {
        double rr[2];           /* same name, array — needs 16 bytes */
        rr[0] = r; rr[1] = 0.0;
        for (int iter = 0; iter < 3; iter++) {
            exp -= 10;
            f2(rr, 1.0e+10, 0.0);
            printf("%d ", exp);
            rr[0] = 0.0;        /* reset so we keep iterating */
        }
    }
    return exp;
}

int main(void) {
    (void)run(1.5);
    printf("\n");
    return 0;
}
