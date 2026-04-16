// TEST: cond_expr_struct
// DESCRIPTION: Conditional expression returning struct must work as rvalue
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's parser-generated code uses:
     yymsp[-10].minor.yy0 = (cond ? struct_a : struct_b);
   The conditional expression returns a struct by value, which is
   then assigned. jmcc reports "expression is not an lvalue". */

int printf(const char *fmt, ...);

typedef struct { int n; int m; } T;

int main(void) {
    T a = {5, 6};
    T b = {10, 20};
    T result;

    /* Assign from conditional that returns struct */
    result = (1 ? a : b);
    if (result.n != 5) return 1;
    if (result.m != 6) return 2;

    result = (0 ? a : b);
    if (result.n != 10) return 3;
    if (result.m != 20) return 4;

    /* Assign to struct member from conditional */
    T target;
    target.n = 0;
    target = (1 ? a : b);
    if (target.n != 5) return 5;

    printf("ok\n");
    return 0;
}
