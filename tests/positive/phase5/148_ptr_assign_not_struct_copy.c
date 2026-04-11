// TEST: ptr_assign_not_struct_copy
// DESCRIPTION: Assigning struct pointers must NOT trigger struct-by-value copy
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Test all lvalue patterns where the target is a struct POINTER
   (not struct by value). The struct copy fix must not trigger on these. */

int printf(const char *fmt, ...);

typedef struct { int x; int y; } point_t;

point_t points[4] = {{1,2},{3,4},{5,6},{7,8}};
point_t *get_point(int i) { return &points[i]; }

/* Various container patterns */
typedef struct {
    point_t *single;
    point_t *arr[4];
} container_t;

container_t g_cont;
container_t *g_ptr;
point_t *g_ptrarr[4];

int main(void) {
    container_t c;
    container_t *cp = &c;
    g_ptr = &c;

    /* 1. ptr->ptr_member = func() */
    cp->single = get_point(0);
    if (cp->single->x != 1) return 1;

    /* 2. ptr->ptr_array[i] = func() */
    int i;
    for (i = 0; i < 4; i++)
        cp->arr[i] = get_point(i);
    if (cp->arr[2]->x != 5) return 2;

    /* 3. global_struct.ptr_member = func() */
    g_cont.single = get_point(3);
    if (g_cont.single->y != 8) return 3;

    /* 4. global_struct.ptr_array[i] = func() */
    g_cont.arr[0] = get_point(1);
    if (g_cont.arr[0]->x != 3) return 4;

    /* 5. global_ptr->ptr_member = func() */
    g_ptr->single = get_point(2);
    if (g_ptr->single->y != 6) return 5;

    /* 6. global_ptr_array[i] = func() */
    for (i = 0; i < 4; i++)
        g_ptrarr[i] = get_point(i);
    if (g_ptrarr[3]->x != 7) return 6;

    /* 7. array_of_structs[i].ptr_member = func() */
    container_t arr[2];
    arr[0].single = get_point(0);
    arr[1].single = get_point(3);
    if (arr[1].single->y != 8) return 7;

    /* 8. Chained: ptr->ptr_member->ptr_member (not assignment, just verify access) */
    /* Already tested elsewhere, just ensure no regression */

    printf("ok\n");
    return 0;
}
