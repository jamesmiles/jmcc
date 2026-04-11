// TEST: func_call_7plus_args
// DESCRIPTION: Function calls with 7+ arguments must pass extras on the stack correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* System V AMD64 ABI: args 1-6 in rdi,rsi,rdx,rcx,r8,r9.
   Args 7+ go on the stack in RIGHT-TO-LEFT order.

   Doom's V_CopyRect(0, 0, 4, 320, 32, 0, 168, 0) has 8 args.
   Args 7 (168) and 8 (0) must be on the stack.

   jmcc pushes all 8 then pops 6 for registers, but the stack
   order is wrong — args 7-8 get consumed by register pops instead
   of staying on the stack for the callee to read. */

int printf(const char *fmt, ...);

int check8(int a, int b, int c, int d, int e, int f, int g, int h) {
    if (a != 0) return 1;
    if (b != 0) return 2;
    if (c != 4) return 3;
    if (d != 320) return 4;
    if (e != 32) return 5;
    if (f != 0) return 6;
    if (g != 168) return 7;   /* arg 7 on stack */
    if (h != 0) return 8;     /* arg 8 on stack */
    return 0;
}

int main(void) {
    /* Exact Doom V_CopyRect pattern */
    int r = check8(0, 0, 4, 320, 32, 0, 168, 0);
    if (r != 0) return r;

    /* Different values for args 7-8 to ensure they're not just 0 */
    r = check8(1, 2, 3, 4, 5, 6, 77, 88);
    if (r != 0) return 10 + r;

    printf("ok\n");
    return 0;
}
