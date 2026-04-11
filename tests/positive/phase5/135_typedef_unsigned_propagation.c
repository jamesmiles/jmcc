// TEST: typedef_unsigned_propagation
// DESCRIPTION: typedef unsigned type must retain unsigned semantics in comparisons
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom uses: typedef unsigned angle_t;
   angle_t variables must compare as unsigned. ANG180 = 0x80000000
   which is negative if treated as signed int. Doom's BSP clipper
   does: if (span >= ANG180) which must be an unsigned comparison.

   If the typedef doesn't propagate unsigned, the comparison
   uses signed setge instead of unsigned setae, giving wrong
   clip results and producing invalid wall column ranges. */

int printf(const char *fmt, ...);

typedef unsigned angle_t;

int main(void) {
    angle_t ang = 0x80000000u;  /* ANG180 */

    /* Comparison: ANG180 >= ANG180 must be true */
    if (!(ang >= 0x80000000u)) return 1;

    /* ANG180 > 0 must be true (unsigned: 2147483648 > 0) */
    if (!(ang > 0)) return 2;

    /* Comparison between two angle_t values */
    angle_t a = 0xC0000000u;  /* 270 degrees */
    angle_t b = 0x40000000u;  /* 90 degrees */
    if (!(a > b)) return 3;   /* 270 > 90 unsigned */

    /* The Doom clipping pattern */
    angle_t clipangle = 0x20000000u;
    angle_t span = 0x90000000u;
    if (span >= 0x80000000u) {
        /* This branch should be taken (span is >= ANG180) */
    } else {
        return 4;  /* Wrong: span treated as negative */
    }

    /* 2*clipangle must not overflow signedness */
    angle_t twoclip = 2 * clipangle;  /* 0x40000000 */
    angle_t tspan = 0x50000000u;
    if (tspan > twoclip) {
        /* Correct: 0x50000000 > 0x40000000 */
    } else {
        return 5;
    }

    /* Right shift on angle_t must be logical (unsigned) */
    angle_t shifted = ang >> 1;
    if (shifted != 0x40000000u) return 6;  /* logical: 0x40000000 */

    printf("ok\n");
    return 0;
}
