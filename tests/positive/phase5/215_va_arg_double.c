// TEST: va_arg_double
// DESCRIPTION: va_arg(ap, double) must read from xmm register save area, not gp
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's printf formats REAL values via `sqlite3_snprintf("%!.15g", d)`
   which eventually calls `va_arg(ap, double)` inside its printf interpreter.

   In the System V AMD64 ABI, the first 8 floating-point args are passed in
   xmm0-xmm7 — NOT in the general-purpose registers. The va_list reg_save_area
   holds TWO saved blocks:
     - 0..47:  gp regs (rdi, rsi, rdx, rcx, r8, r9)
     - 48..175: xmm0..xmm7 (16 bytes each)

   va_arg(ap, double) must use fp_offset (start at 48, max 176) to index into
   the xmm portion. jmcc instead uses gp_offset for doubles, reading from the
   GP area — which holds unrelated named-arg values — producing garbage.

   This causes SQLite to render REAL column values as garbage like
   "4.86e-310" instead of "3.14". */

#include <stdarg.h>
#include <stdio.h>

double pick1(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    double r = va_arg(ap, double);
    va_end(ap);
    return r;
}

double pick2(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    double a = va_arg(ap, double);
    double b = va_arg(ap, double);
    va_end(ap);
    return a + b;
}

/* Mixed: int, then double — int goes in GP, double goes in xmm */
double mixed(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int n = va_arg(ap, int);
    double d = va_arg(ap, double);
    va_end(ap);
    return (double)n + d;
}

int main(void) {
    double x = pick1("%g", 3.14);
    if (x != 3.14) { printf("fail1 got %g\n", x); return 1; }

    double y = pick2("%g%g", 1.5, 2.5);
    if (y != 4.0) { printf("fail2 got %g\n", y); return 2; }

    double z = mixed("%d%g", 7, 0.25);
    if (z != 7.25) { printf("fail3 got %g\n", z); return 3; }

    printf("ok\n");
    return 0;
}
