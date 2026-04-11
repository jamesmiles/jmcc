// TEST: func_call_7plus_args
// DESCRIPTION: Function calls with 7+ arguments must pass extras on the stack correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* System V AMD64 ABI: args 1-6 in rdi,rsi,rdx,rcx,r8,r9.
   Args 7+ go on the stack in RIGHT-TO-LEFT order. */

int printf(const char *fmt, ...);

int sum8(int a, int b, int c, int d, int e, int f, int g, int h) {
    return a + b + c + d + e + f + g + h;
}

int verify8(int a, int b, int c, int d, int e, int f, int g, int h) {
    if (g != 77) return 1;
    if (h != 88) return 2;
    if (a != 1) return 3;
    if (f != 6) return 4;
    return 0;
}

int main(void) {
    /* Basic sum with 8 args */
    int r = sum8(1, 2, 3, 4, 5, 6, 7, 8);
    if (r != 36) return 1;

    /* Verify specific stack args (7 and 8) have correct values */
    r = verify8(1, 2, 3, 4, 5, 6, 77, 88);
    if (r != 0) return 10 + r;

    /* 7 args */
    int sum7(int a, int b, int c, int d, int e, int f, int g);
    r = sum7(10, 20, 30, 40, 50, 60, 70);
    if (r != 280) return 20;

    printf("ok\n");
    return 0;
}

int sum7(int a, int b, int c, int d, int e, int f, int g) {
    return a + b + c + d + e + f + g;
}
