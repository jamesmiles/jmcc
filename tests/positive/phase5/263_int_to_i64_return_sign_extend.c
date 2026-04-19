// TEST: int_to_i64_return_sign_extend
// DESCRIPTION: returning int from i64 function must sign-extend, not zero-extend
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdint.h>

typedef int64_t i64;
typedef int8_t i8;
typedef uint8_t u8;

#define TWO_BYTE_INT(x)    (256*(i8)((x)[0])|(x)[1])
#define THREE_BYTE_INT(x)  (65536*(i8)((x)[0])|((x)[1]<<8)|(x)[2])

static i64 decode2(const u8 *x) { return TWO_BYTE_INT(x); }
static i64 decode3(const u8 *x) { return THREE_BYTE_INT(x); }

/* Also test plain int-expression returns */
static i64 negate_int(int v) { return -v; }
static i64 mul_int(int a, int b) { return a * b; }

int main(void) {
    int ok = 1;

    /* Two-byte: -32768 = {0x80, 0x00} */
    u8 b2[] = {0x80, 0x00};
    i64 r2 = decode2(b2);
    if (r2 != -32768LL) {
        printf("FAIL: TWO_BYTE_INT(-32768) = %lld expected -32768\n", (long long)r2);
        ok = 0;
    }

    /* Three-byte: -8388608 = {0x80, 0x00, 0x00} */
    u8 b3[] = {0x80, 0x00, 0x00};
    i64 r3 = decode3(b3);
    if (r3 != -8388608LL) {
        printf("FAIL: THREE_BYTE_INT(-8388608) = %lld expected -8388608\n", (long long)r3);
        ok = 0;
    }

    /* Plain int return from i64 function */
    i64 r4 = negate_int(100);
    if (r4 != -100LL) {
        printf("FAIL: negate_int(100) = %lld expected -100\n", (long long)r4);
        ok = 0;
    }

    i64 r5 = mul_int(-1000, 1000);
    if (r5 != -1000000LL) {
        printf("FAIL: mul_int(-1000,1000) = %lld expected -1000000\n", (long long)r5);
        ok = 0;
    }

    /* Compare: must all be < 16384 */
    if (r2 >= 16384) { printf("FAIL: -32768 should be < 16384\n"); ok = 0; }
    if (r3 >= 16384) { printf("FAIL: -8388608 should be < 16384\n"); ok = 0; }

    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
