// TEST: attribute_after_declarator
// DESCRIPTION: __attribute__ appearing after a declarator (before the semicolon) must work, e.g. void (*fp)(int) __attribute__((common))
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

/* function pointer variable with __attribute__ after the declarator */
void *(*my_alloc)(int size) __attribute__((__common__));
void (*my_free)(void *ptr) __attribute__((__common__));

int main(void) {
    (void)my_alloc;
    (void)my_free;
    printf("OK\n");
    return 0;
}
