// TEST: int128_shift_print
// DESCRIPTION: __int128 bit shifts and decimal printing via digit extraction
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Bit shifts on __int128: left shift uses shld+shl, right shift uses
   shrd+shr (logical) or shrd+sar (arithmetic).

   Decimal printing of __int128 (there is no printf format for it) uses
   repeated % 10 / 10, exactly as in print128() in the Rosetta task. */

#include <stdio.h>
#include <string.h>

static void print128(__int128 n, char *out) {
    char buf[40];
    int pos = 39;
    int negative = 0;
    buf[pos] = '\0';
    if (n == 0) { out[0]='0'; out[1]='\0'; return; }
    if (n < 0) { negative = 1; n = -n; }
    while (n > 0) {
        buf[--pos] = '0' + (int)(n % 10);
        n /= 10;
    }
    if (negative) buf[--pos] = '-';
    strcpy(out, &buf[pos]);
}

int main(void) {
    char buf[40];

    /* left shift: 1 << 64 should give 2^64 */
    __int128 one64 = (__int128)1 << 64;
    if ((unsigned long long)(one64 >> 64) != 1 || (unsigned long long)one64 != 0) {
        printf("FAIL <<64\n"); return 1;
    }

    /* right shift */
    __int128 x = (__int128)3 << 64;
    __int128 rsh = x >> 1;
    if ((unsigned long long)(rsh >> 64) != 1) { printf("FAIL >>1 hi\n"); return 2; }
    if ((unsigned long long)rsh != (1ULL << 63)) { printf("FAIL >>1 lo\n"); return 3; }

    /* print small value */
    print128(0, buf);
    if (strcmp(buf, "0") != 0) { printf("FAIL print 0: %s\n", buf); return 4; }

    print128(42, buf);
    if (strcmp(buf, "42") != 0) { printf("FAIL print 42: %s\n", buf); return 5; }

    print128(-1, buf);
    if (strcmp(buf, "-1") != 0) { printf("FAIL print -1: %s\n", buf); return 6; }

    /* print value > 2^63 (needs full 128-bit division) */
    __int128 big = (__int128)99 * ((__int128)1000000000LL * 1000000000LL);  /* 99e18 */
    print128(big, buf);
    if (strcmp(buf, "99000000000000000000") != 0) {
        printf("FAIL print big: %s\n", buf); return 7;
    }

    /* print the 27-digit number from the Rosetta task:
       111111111111111111111111111 */
    __int128 n27 = 0;
    int i;
    for (i = 0; i < 27; i++) { n27 = n27 * 10 + 1; }
    print128(n27, buf);
    if (strcmp(buf, "111111111111111111111111111") != 0) {
        printf("FAIL print 27: %s\n", buf); return 8;
    }

    printf("ok\n");
    return 0;
}
