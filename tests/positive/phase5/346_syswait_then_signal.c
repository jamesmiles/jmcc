// TEST: syswait_then_signal
// DESCRIPTION: Including sys/wait.h before signal.h must not break siginfo_t (sys/wait.h
//              pulls in bits/types/siginfo_t.h which redefines siginfo_t with nested
//              anonymous unions that jmcc cannot parse)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>

int main(void) {
    siginfo_t info;
    info.si_code = SI_USER;
    (void)info;
    printf("OK\n");
    return 0;
}
