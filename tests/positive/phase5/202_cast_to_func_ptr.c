// TEST: cast_to_func_ptr
// DESCRIPTION: Cast expression with function pointer target type must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite casts function pointers loaded from a syscall dispatch table:
     return ((uid_t(*)(void))aSyscall[21].pCurrent)() ? 0 : ...;
   The type (uid_t(*)(void)) is a cast target: function pointer type
   spelled as "return_type(*)(params)". jmcc can't parse this form
   in a cast expression. */

int printf(const char *fmt, ...);

typedef unsigned int uid_t;

uid_t getval(void) { return 42; }
int add_two(int a, int b) { return a + b; }

int main(void) {
    /* Test 1: cast void* to function pointer with typedef'd return type */
    void *p1 = (void *)getval;
    uid_t r1 = ((uid_t(*)(void))p1)();
    if (r1 != 42) return 1;

    /* Test 2: cast with parameters */
    void *p2 = (void *)add_two;
    int r2 = ((int(*)(int, int))p2)(3, 4);
    if (r2 != 7) return 2;

    /* Test 3: store cast in a variable (not just call) */
    int (*fp)(void) = (int(*)(void))p1;
    if (fp() != 42) return 3;

    /* Test 4: dispatch table pattern (SQLite's exact usage) */
    void *table[2];
    table[0] = (void *)getval;
    table[1] = (void *)add_two;
    int r4 = ((int(*)(void))table[0])();
    if (r4 != 42) return 4;

    printf("ok\n");
    return 0;
}
