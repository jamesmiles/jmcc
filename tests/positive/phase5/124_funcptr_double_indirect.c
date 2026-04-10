// TEST: funcptr_double_indirect
// DESCRIPTION: Calling through pointer-to-function-pointer must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's wipe code and thinker system use patterns like:
     void (*func)(args) = *table_ptr;
     func(args);
   or: (*ptr_to_func_ptr)(args)
   The double indirection must load the function address correctly
   as a 64-bit pointer before calling. */

int printf(const char *fmt, ...);

int add(int a, int b) { return a + b; }

typedef int (*binop_t)(int, int);

binop_t g_func;

int main(void) {
    /* Store function pointer in global */
    g_func = add;

    /* Call through pointer-to-function-pointer */
    binop_t *pp = &g_func;
    int result = (*pp)(7, 8);
    if (result != 15) return 1;

    /* Array of function pointers, accessed via pointer */
    binop_t arr[2];
    arr[0] = add;
    binop_t *p = &arr[0];
    result = (*p)(3, 4);
    if (result != 7) return 2;

    printf("ok\n");
    return 0;
}
