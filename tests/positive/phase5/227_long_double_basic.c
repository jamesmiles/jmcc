// TEST: long_double_basic
// DESCRIPTION: long double literals and %Lf printf format must produce correct values
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* jmcc treats `long double` as `double` size/ABI wise, but printf's
   variadic argument handling for %Lf expects a 16-byte (on x86-64
   Linux) long double. When jmcc passes only 8 bytes but printf reads
   16, the result is NaN and subsequent arguments are shifted by 8
   bytes, so every later `%d`/`%c` prints garbage.

   Reduced from rosettacode/implicit_type_conversion whose printf is:

       printf("%LF ... bytes from '%c'\n",
              llf=(lf=(i=(si=c))), sizeof llf, ..., c);

   jmcc prints `0.000000 ... from ' '` (space) instead of `49.000000
   ... from '1'` because the long-double arg size mismatch shifts all
   the later arguments. */

#include <stdio.h>
#include <string.h>

int main(void) {
    /* Direct long double literal */
    long double ld = 49.0L;
    char buf[64];
    snprintf(buf, sizeof(buf), "%Lf", ld);
    /* Accept either "49.000000" or "49.0" or similar — NOT "nan"/"0.0" */
    if (buf[0] != '4' || buf[1] != '9') {
        printf("FAIL %%Lf: [%s] expected 49.*\n", buf);
        return 1;
    }

    /* Mixed argument sizes after a long double: the next int argument
       must NOT be mis-read as the upper half of the long double. */
    int marker = 0x12345678;
    char c = '!';
    snprintf(buf, sizeof(buf), "%Lf %d %c", 1.5L, marker, c);
    /* Must contain "305419896" (dec of 0x12345678) and '!' */
    char expect_marker[16];
    snprintf(expect_marker, sizeof(expect_marker), "%d", marker);
    if (!strstr(buf, expect_marker)) {
        printf("FAIL marker missing: [%s]\n", buf);
        return 2;
    }
    if (!strchr(buf, '!')) {
        printf("FAIL char missing: [%s]\n", buf);
        return 3;
    }

    printf("ok\n");
    return 0;
}
