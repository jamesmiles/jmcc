// TEST: signal_stack_t
// DESCRIPTION: stack_t type and SIGSTKSZ constant from signal.h must be defined
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <signal.h>

int main(void) {
    stack_t alt_stack;
    alt_stack.ss_sp = NULL;
    alt_stack.ss_flags = SS_DISABLE;
    alt_stack.ss_size = SIGSTKSZ;
    (void)alt_stack;
    printf("OK\n");
    return 0;
}
