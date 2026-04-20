// TEST: double_paren_typedef_shadow
// DESCRIPTION: ((typedef_var)->member) with extra parens must not be misread as cast
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef struct list { int len; struct list *next; } list;

static int total_len(const list *list) {
    int sum = 0;
    while ((( list )->len) > 0) {
        sum += (( list )->len);
        list = (( list )->next);
        if (!list) break;
    }
    return sum;
}

int main(void) {
    list b = {3, NULL};
    list a = {7, &b};
    int t = total_len(&a);
    if (t != 10) return 1;  /* processes both nodes: 7 + 3 = 10 */
    printf("OK\n");
    return 0;
}
