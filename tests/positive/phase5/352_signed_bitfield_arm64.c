// TEST: signed_bitfield_arm64
// DESCRIPTION: Signed bitfield reads must sign-extend the extracted value on arm64.
// A signed int bitfield stores -3 as 0b1101 (13 unsigned). Reading it back
// must produce -3, not 13. jmcc was using ubfx-equivalent (and+mask) for all
// bitfields, treating them as unsigned regardless of the declared type.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -3 12 -1 -8 7
// ENVIRONMENT: hosted
// PHASE: 5

// ARM64 divergence: x86-64 CI had the same bug fixed simultaneously in the
// x86-64 backend; this test is arm64-specific to isolate arm64 regressions.

#include <stdio.h>

struct Mixed {
    signed int   sx : 4;   /* -8..7  */
    unsigned int ux : 4;   /* 0..15  */
    int          sign : 1; /* -1..0  */
    signed int   edge_neg : 4; /* test min value -8 */
    signed int   edge_pos : 4; /* test max value 7 */
};

int main(void) {
    struct Mixed f;
    f.sx       = -3;
    f.ux       = 12;
    f.sign     = -1;
    f.edge_neg = -8;   /* min for 4-bit signed: 0b1000 */
    f.edge_pos = 7;    /* max for 4-bit signed: 0b0111 */

    printf("%d %u %d %d %d\n", f.sx, f.ux, f.sign, f.edge_neg, f.edge_pos);

    if (f.sx       != -3) return 1;
    if (f.ux       != 12) return 2;
    if (f.sign     != -1) return 3;
    if (f.edge_neg != -8) return 4;
    if (f.edge_pos !=  7) return 5;
    return 0;
}
