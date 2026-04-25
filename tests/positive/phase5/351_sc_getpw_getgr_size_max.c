// TEST: sc_getpw_getgr_size_max
// DESCRIPTION: _SC_GETPW_R_SIZE_MAX and _SC_GETGR_R_SIZE_MAX must be defined in unistd.h (used by CPython pwdmodule.c, grpmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <unistd.h>
#include <stdio.h>

int main(void) {
    long pw = sysconf(_SC_GETPW_R_SIZE_MAX);
    long gr = sysconf(_SC_GETGR_R_SIZE_MAX);
    (void)pw; (void)gr;
    printf("OK\n");
    return 0;
}
