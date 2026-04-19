// TEST: vararg_double_int_overflow
// DESCRIPTION: when int regs are full, double (xmm0) must not occupy stack overflow slot before int overflow args
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdarg.h>

/* Callee: 2 named params + 7 variadic (4 int regs, 2 int overflow, 1 double xmm0) */
static void check(int named1, int named2, ...) {
    va_list ap;
    va_start(ap, named2);
    int a1 = va_arg(ap, int);    /* rdx */
    int a2 = va_arg(ap, int);    /* rcx */
    int a3 = va_arg(ap, int);    /* r8  */
    int a4 = va_arg(ap, int);    /* r9  */
    int a5 = va_arg(ap, int);    /* stack overflow[0]: must be h, not double bits */
    int a6 = va_arg(ap, int);    /* stack overflow[8]: must be m */
    double a7 = va_arg(ap, double); /* xmm0 */
    va_end(ap);
    if (a5 != 7 || a6 != 13) {
        printf("FAIL a5=%d a6=%d a7=%f (expected h=7 m=13)\n", a5, a6, a7);
    } else if (a7 < 1.4 || a7 > 1.6) {
        printf("FAIL a7=%f (expected ~1.5)\n", a7);
    } else {
        printf("ok\n");
    }
}

int main(void) {
    /* Caller must NOT put 1.5 at stack[0] before h=7 and m=13.
       x86-64 SysV: double goes in xmm0 (not in stack overflow area);
       int overflow args start at stack[0]. */
    check(100, 200, 1, 2, 3, 4, 7, 13, 1.5);
    return 0;
}
