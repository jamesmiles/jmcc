// TEST: ptr_const_ptr_multi_decl
// DESCRIPTION: char *const * in a multi-variable declaration must parse correctly (used by CPython _posixsubprocess.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

int main(void) {
    char *const *argv = (void *)0, *const *envp = (void *)0;
    (void)argv; (void)envp;
    printf("OK\n");
    return 0;
}
