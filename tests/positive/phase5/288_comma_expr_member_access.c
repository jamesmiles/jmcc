// TEST: comma_expr_member_access
// DESCRIPTION: member access on a comma expression result must use the type of the right operand
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
typedef struct { int x; } T;

int main(void) {
    T obj; obj.x = 42;
    T *p = &obj;
    /* comma expression result used for -> member access */
    int v = ((void)0, p)->x;
    if (v != 42) return 1;
    /* double nested */
    int w = ((void)0, ((void)0, p))->x;
    if (w != 42) return 2;
    printf("OK\n");
    return 0;
}
