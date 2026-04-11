// TEST: struct_assign_regression
// DESCRIPTION: Struct copy fix must not break non-struct assignments or member access
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* The rep movsb fix for struct assignment might over-trigger on
   non-struct expressions, causing "expression is not an lvalue"
   errors. Test that normal assignments still compile and work. */

int printf(const char *fmt, ...);

struct point { int x; int y; };

struct container {
    struct point pos;
    int value;
    struct point *ptr;
};

int main(void) {
    /* Normal int assignments */
    int a = 10;
    int b = a;
    if (b != 10) return 1;

    /* Struct member assignment (not struct copy) */
    struct container c;
    c.pos.x = 100;
    c.pos.y = 200;
    c.value = 42;
    if (c.pos.x != 100) return 2;

    /* Struct pointer member */
    struct point p = {5, 6};
    c.ptr = &p;
    if (c.ptr->x != 5) return 3;

    /* Actual struct copy (should work) */
    struct container d;
    d = c;
    if (d.pos.x != 100) return 4;
    if (d.value != 42) return 5;

    /* Nested struct member copy */
    struct point q;
    q = c.pos;
    if (q.x != 100) return 6;
    if (q.y != 200) return 7;

    printf("ok\n");
    return 0;
}
