// TEST: signed_char_to_i64_sign_extend
// DESCRIPTION: signed char (i8) cast to long long must sign-extend through 64 bits not just 32
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef signed char i8;
typedef long long i64;
typedef unsigned char u8;

/* Return an i8 value as i64 — jmcc was zero-extending the 32-bit movsbl result
   via eax->rax, giving 0x00000000FFFFFFFF instead of 0xFFFFFFFFFFFFFFFF */
static i64 decode_byte(const u8 *aKey) {
    return (i8)(aKey[0]);
}

/* Trigger via arithmetic comparison (mirrors sqlite3VdbeRecordCompareWithSkip) */
static int compare_neg(const u8 *aKey) {
    i64 lhs = (i8)(aKey[0]);  /* should be -1 */
    i64 rhs = 0;
    if (lhs < rhs) return -1;
    if (lhs > rhs) return +1;
    return 0;
}

int main(void) {
    u8 neg_one[] = {0xFF};  /* -1 as signed byte */
    u8 plus_one[] = {0x01};
    u8 zero_byte[] = {0x00};

    i64 r1 = decode_byte(neg_one);
    i64 r2 = decode_byte(plus_one);
    i64 r3 = decode_byte(zero_byte);

    if (r1 != -1LL) {
        printf("FAIL: decode(0xFF) as i64 = %lld expected -1\n", r1);
        return 1;
    }
    if (r2 != 1LL) {
        printf("FAIL: decode(0x01) as i64 = %lld expected 1\n", r2);
        return 1;
    }
    if (r3 != 0LL) {
        printf("FAIL: decode(0x00) as i64 = %lld expected 0\n", r3);
        return 1;
    }
    /* Also test comparison (the sqlite3 code path that actually broke) */
    if (compare_neg(neg_one) != -1) {
        printf("FAIL: compare_neg(0xFF)=%d expected -1 (i.e. -1<0)\n", compare_neg(neg_one));
        return 1;
    }
    printf("ok\n");
    return 0;
}
