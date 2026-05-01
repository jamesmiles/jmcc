// TEST: signed_bitfield_read
// DESCRIPTION: Signed integer bitfield reads must sign-extend the extracted bits.
// A signed int bitfield containing -3 is stored as 0b1101 in the unit; reading
// it must yield -3 (not 13). jmcc was using unsigned masking for all bitfields
// regardless of declared signedness.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -3 12 -1 -8 7
// ENVIRONMENT: hosted
// PHASE: 5

#include <stdio.h>

struct Mixed {
    signed int   sx  : 4;   /* -8..7  */
    unsigned int ux  : 4;   /* 0..15  */
    int          s1  : 1;   /* -1..0  */
    signed int   smin: 4;   /* test min: -8 */
    signed int   smax: 4;   /* test max:  7 */
};

int main(void) {
    struct Mixed f;
    f.sx   = -3;
    f.ux   = 12;
    f.s1   = -1;
    f.smin = -8;
    f.smax =  7;

    printf("%d %u %d %d %d\n", f.sx, f.ux, f.s1, f.smin, f.smax);

    if (f.sx   != -3) return 1;
    if (f.ux   != 12) return 2;
    if (f.s1   != -1) return 3;
    if (f.smin != -8) return 4;
    if (f.smax !=  7) return 5;
    return 0;
}
