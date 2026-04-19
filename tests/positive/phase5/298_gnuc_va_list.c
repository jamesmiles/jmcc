// TEST: gnuc_va_list
// DESCRIPTION: __gnuc_va_list must be defined in stdarg.h as typedef for __builtin_va_list
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdarg.h>

extern void my_vlog(const char *fmt, __gnuc_va_list ap);
void my_vlog(const char *fmt, __gnuc_va_list ap) {
    vprintf(fmt, ap);
}

static void my_log(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    my_vlog(fmt, ap);
    va_end(ap);
}

int main(void) {
    my_log("%s\n", "OK");
    return 0;
}
