// TEST: var_shadows_typedef
// DESCRIPTION: local variable with same name as typedef must shadow the typedef in that scope
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdlib.h>

typedef struct node { int val; } node;

/* variable 'node' shadows typedef 'node' inside this function */
static node *make(int v) {
    struct node *node;
    if ((node = malloc(sizeof(*node))) == NULL) return NULL;
    node->val = v;
    return node;
}

int main(void) {
    node *p;
    if ((p = make(99)) == NULL) return 1;
    if (p->val != 99) return 2;
    free(p);
    printf("OK\n");
    return 0;
}
