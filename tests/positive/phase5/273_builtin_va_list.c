/* __builtin_va_list must be recognized as a built-in type specifier.
   GCC exposes it in stdarg.h as: typedef __builtin_va_list __gnuc_va_list;
   Without this, any file that includes <stdarg.h> fails to compile. */
#include <stdio.h>
#include <stdarg.h>

static int sum(int n, ...) {
    va_list ap;
    va_start(ap, n);
    int total = 0;
    for (int i = 0; i < n; i++)
        total += va_arg(ap, int);
    va_end(ap);
    return total;
}

int main(void) {
    /* Also test the raw typedef path used by GCC's stdarg.h */
    typedef __builtin_va_list my_va_list;
    if (sum(3, 10, 20, 30) != 60) return 1;
    printf("OK\n");
    return 0;
}
