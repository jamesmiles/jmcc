// TEST: int32_to_int64_sign_extend
// DESCRIPTION: 32-bit int arithmetic result assigned to i64 struct field must sign-extend
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c sqlite3VdbeSerialGet case 4 (FOUR_BYTE_INT):
     pMem->u.i = 16777216*(i8)buf[0] | (buf[1]<<16) | (buf[2]<<8) | buf[3];
   Bug: 32-bit int expression (orl result) is zero-extended when stored to
   the i64 field pMem->u.i. For -3 (0xFFFFFFFD), this produces 4294967293.
   Fix: emit movslq to sign-extend int->i64 before the movq store. */

#include <stdio.h>
typedef long long i64;

struct Mem { i64 i; };

int main(void) {
    struct Mem m;

    /* 32-bit int bitwise OR produces 0xFFFFFFFD = -3; must sign-extend to i64 */
    int a = 0xFF000000;
    int b = 0x00FFFFFD;
    m.i = a | b;

    if (m.i != -3LL) {
        printf("FAIL: m.i=%lld (expected -3)\n", (long long)m.i);
        return 1;
    }

    /* also test with negation */
    int x = 3;
    m.i = -x;
    if (m.i != -3LL) {
        printf("FAIL: neg m.i=%lld (expected -3)\n", (long long)m.i);
        return 1;
    }

    printf("ok\n");
    return 0;
}
