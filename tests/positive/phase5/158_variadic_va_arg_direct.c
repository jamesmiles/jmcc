// TEST: variadic_va_arg_direct
// DESCRIPTION: Direct va_arg reads must return correct values for all types
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Test va_arg directly (not through vprintf).
   This exercises the va_list gp_offset/reg_save_area
   walking that happens when reading args one by one. */

#include <stdarg.h>

int printf(const char *fmt, ...);

/* Read ints via va_arg */
int sum_ints(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int total = 0;
    for (int i = 0; i < count; i++)
        total += va_arg(ap, int);
    va_end(ap);
    return total;
}

/* Read mixed types via va_arg */
long mixed_args(int count, ...) {
    va_list ap;
    va_start(ap, count);
    long result = 0;
    for (int i = 0; i < count; i++) {
        int type = va_arg(ap, int);
        if (type == 0)
            result += va_arg(ap, int);
        else if (type == 1)
            result += va_arg(ap, long);
        else if (type == 2) {
            char *s = va_arg(ap, char *);
            result += s[0];  /* just use first char */
        }
    }
    va_end(ap);
    return result;
}

/* Read pointers via va_arg */
int sum_via_ptrs(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int total = 0;
    for (int i = 0; i < count; i++) {
        int *p = va_arg(ap, int *);
        total += *p;
    }
    va_end(ap);
    return total;
}

int main(void) {
    /* Test 1: single int */
    if (sum_ints(1, 42) != 42) return 1;

    /* Test 2: multiple ints in registers */
    if (sum_ints(4, 10, 20, 30, 40) != 100) return 2;

    /* Test 3: 6+ variadic ints (overflow to stack) */
    if (sum_ints(8, 1, 2, 3, 4, 5, 6, 7, 8) != 36) return 3;

    /* Test 4: mixed int and string types */
    /* type=0(int) val=100, type=2(str) val="A"(65) */
    long r = mixed_args(2, 0, 100, 2, "A");
    if (r != 165) return 4;

    /* Test 5: pointer arguments */
    int a = 10, b = 20, c = 30;
    if (sum_via_ptrs(3, &a, &b, &c) != 60) return 5;

    /* Test 6: many args that overflow registers */
    if (sum_ints(10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) != 10) return 6;

    printf("ok\n");
    return 0;
}
