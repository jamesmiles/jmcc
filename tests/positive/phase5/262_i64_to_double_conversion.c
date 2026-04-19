// TEST: i64_to_double_conversion
// DESCRIPTION: int64_t to double conversion must use 64-bit cvtsi2sdq not 32-bit cvtsi2sd
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdint.h>

/* Bug: jmcc emits cvtsi2sd %eax (32-bit) instead of cvtsi2sdq %rax (64-bit)
   when converting int64_t to double, so large values lose their upper 32 bits.
   Symptom: sqlite3's julianday('2000-01-01') returns -16.87 instead of 2451544.5
   because iJD=211813444800000 is converted using only the low 32 bits (-1457336832),
   then divided by 86400000.0 giving -16.87 */

static double i64_to_double(int64_t x) { return (double)x; }

int main(void) {
    /* 211813444800000 = 2451544.5 * 86400000 (SQLite Julian day for 2000-01-01) */
    int64_t v1 = 211813444800000LL;
    double d1 = i64_to_double(v1);
    if (d1 < 2.118134e14 || d1 > 2.118135e14) {
        printf("FAIL: (double)211813444800000 = %.15g expected ~2.11813e14\n", d1);
        return 1;
    }

    /* Direct division that sqlite3 does: iJD / 86400000.0 */
    double jd = v1 / 86400000.0;
    if (jd < 2451544.4 || jd > 2451544.6) {
        printf("FAIL: iJD/86400000.0 = %.15g expected 2451544.5\n", jd);
        return 1;
    }

    /* 2^33: > INT32_MAX, lower 32 bits are 0 - sign would be positive but truncated to 0 */
    int64_t v2 = 8589934592LL; /* 2^33 */
    double d2 = i64_to_double(v2);
    if (d2 < 8.58e9 || d2 > 8.60e9) {
        printf("FAIL: (double)2^33 = %.15g expected ~8.59e9\n", d2);
        return 1;
    }

    /* Largest positive int64: 2^63-1 */
    int64_t v3 = 9223372036854775807LL;
    double d3 = i64_to_double(v3);
    if (d3 < 9.22e18 || d3 > 9.24e18) {
        printf("FAIL: (double)INT64_MAX = %.15g expected ~9.22e18\n", d3);
        return 1;
    }

    printf("ok\n");
    return 0;
}
