// TEST: typedef_scope_restore
// DESCRIPTION: when a local variable shadows a typedef, the typedef must be visible again after the block exits
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdlib.h>

typedef struct node { int val; struct node *next; } list;

int main(void) {
    /* local variable shadows typedef 'list' inside this block */
    {
        list *list = malloc(sizeof(struct node));
        list->val = 1;
        list->next = NULL;
        free(list);
    }
    /* after the block, 'list' must be the typedef again */
    list *node = malloc(sizeof(list));
    node->val = 42;
    node->next = NULL;
    if (node->val != 42) return 1;
    free(node);
    printf("OK\n");
    return 0;
}
