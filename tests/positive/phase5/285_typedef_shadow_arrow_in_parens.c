// TEST: typedef_shadow_arrow_in_parens
// DESCRIPTION: (typedef_var->member) must parse as member access, not cast, when var shadows typedef
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef struct node { int val; struct node *next; } node;
typedef struct list { node *head; int len; } list;

static int sum(const list *list) {
    /* (list->head) — 'list' is param name shadowing typedef */
    node *cur = (list->head);
    int total = 0;
    while (cur) {
        total += (cur->val);  /* same pattern with 'node' not shadowed */
        cur = cur->next;
    }
    return total;
}

int main(void) {
    node n2 = {10, NULL};
    node n1 = {5, &n2};
    list l = {&n1, 2};
    int s = sum(&l);
    if (s != 15) return 1;
    printf("OK\n");
    return 0;
}
