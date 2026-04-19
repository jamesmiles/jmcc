// TEST: paren_func_type_typedef
// DESCRIPTION: typedef void (FnName)(params) with parenthesized name must work (used in Redis dict.h)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

/* Parenthesized function-type typedef (different from test 279 which has no parens) */
typedef void (ScanFn)(void *priv, int val);
typedef void *(AllocFn)(void *ptr);
typedef int (CmpFn)(const void *a, const void *b);

static int scan_called = 0;
static void my_scan(void *priv, int val) { (void)priv; (void)val; scan_called = 1; }

static int my_cmp(const void *a, const void *b) {
    return *(int*)a - *(int*)b;
}

int main(void) {
    ScanFn *fp = my_scan;
    fp(NULL, 42);
    if (!scan_called) return 1;

    CmpFn *cp = my_cmp;
    int x = 1, y = 2;
    if (cp(&x, &y) >= 0) return 2;

    printf("OK\n");
    return 0;
}
