// TEST: variadic_va_copy
// DESCRIPTION: va_copy must duplicate va_list state correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* va_copy duplicates a va_list so you can iterate twice.
   This requires correctly copying all 4 fields of the
   AMD64 va_list struct (gp_offset, fp_offset,
   overflow_arg_area, reg_save_area). */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/* Format into buf, then return the length using va_copy */
int format_and_len(char *buf, const char *fmt, ...) {
    va_list ap, ap2;
    va_start(ap, fmt);
    va_copy(ap2, ap);

    /* First pass: format into buffer */
    vsprintf(buf, fmt, ap);
    va_end(ap);

    /* Second pass: format into temp to get length */
    char tmp[256];
    int len = vsprintf(tmp, fmt, ap2);
    va_end(ap2);

    return len;
}

/* Use va_copy after consuming some args */
int sum_twice(int n, ...) {
    va_list ap, ap2;
    va_start(ap, n);

    /* Consume first arg */
    int first = va_arg(ap, int);

    /* Copy after consuming one arg */
    va_copy(ap2, ap);

    /* Sum remaining from ap */
    int sum1 = first;
    for (int i = 1; i < n; i++)
        sum1 += va_arg(ap, int);
    va_end(ap);

    /* Sum remaining from ap2 (should start from second arg) */
    int sum2 = 0;
    for (int i = 1; i < n; i++)
        sum2 += va_arg(ap2, int);
    va_end(ap2);

    /* sum1 should equal first + sum2 */
    if (sum1 != first + sum2) return -1;
    return sum1;
}

int printf(const char *fmt, ...);

int main(void) {
    char buf[256];

    /* Test 1: basic va_copy with vsprintf */
    int len = format_and_len(buf, "x=%d", 99);
    if (strcmp(buf, "x=99") != 0) return 1;
    if (len != 4) return 2;

    /* Test 2: va_copy with multiple args */
    len = format_and_len(buf, "%d+%d=%d", 3, 4, 7);
    if (strcmp(buf, "3+4=7") != 0) return 3;
    if (len != 5) return 4;

    /* Test 3: va_copy after partial consumption */
    int r = sum_twice(4, 10, 20, 30, 40);
    if (r != 100) return 5;

    /* Test 4: va_copy with string args */
    len = format_and_len(buf, "%s=%s", "key", "val");
    if (strcmp(buf, "key=val") != 0) return 6;
    if (len != 7) return 7;

    printf("ok\n");
    return 0;
}
