// TEST: thread_local_storage
// DESCRIPTION: __thread and _Thread_local must be accepted as storage class specifiers (used by CPython pystate.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
/* __thread and _Thread_local (C11) must be supported as storage class specifiers.
   CPython uses __thread for thread-local state (pystate.c).
   Without these, CPython fails to compile with "no supported thread-local
   variable storage classifier". */
#include <stdio.h>

__thread int tls_a = 0;
_Thread_local int tls_b = 99;

static __thread int tls_c = 7;

int main(void) {
    tls_a = 1;
    tls_b = 2;
    tls_c = 3;
    if (tls_a != 1) return 1;
    if (tls_b != 2) return 2;
    if (tls_c != 3) return 3;
    printf("OK\n");
    return 0;
}
