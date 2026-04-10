// TEST: function_pointer_64bit
// DESCRIPTION: Function pointers must be 8 bytes, stored/loaded/called correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom uses function pointers extensively (thinker callbacks, column
   drawers, floor/ceiling functions). They must be 8 bytes on 64-bit. */

int printf(const char *fmt, ...);

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

typedef int (*binop_t)(int, int);

/* Global function pointer */
binop_t g_op = 0;

/* Array of function pointers */
binop_t ops[3];

/* Struct with function pointer */
struct callback {
    int id;
    binop_t func;
};

/* Function returning function pointer */
binop_t get_op(int which) {
    if (which == 0) return add;
    if (which == 1) return sub;
    return mul;
}

int main(void) {
    /* 1. sizeof function pointer */
    if (sizeof(binop_t) != 8) return 1;
    if (sizeof(void (*)(void)) != 8) return 2;

    /* 2. Global function pointer */
    g_op = add;
    if (g_op(10, 3) != 13) return 3;
    g_op = sub;
    if (g_op(10, 3) != 7) return 4;

    /* 3. Array of function pointers */
    ops[0] = add;
    ops[1] = sub;
    ops[2] = mul;
    if (ops[0](5, 3) != 8) return 5;
    if (ops[1](5, 3) != 2) return 6;
    if (ops[2](5, 3) != 15) return 7;

    /* 4. Struct with function pointer */
    struct callback cb;
    cb.id = 42;
    cb.func = mul;
    if (cb.func(6, 7) != 42) return 8;

    /* 5. Function returning function pointer */
    binop_t f = get_op(0);
    if (f(100, 1) != 101) return 9;
    f = get_op(2);
    if (f(10, 20) != 200) return 10;

    printf("ok\n");
    return 0;
}
