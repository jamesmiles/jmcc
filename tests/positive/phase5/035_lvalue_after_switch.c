// TEST: lvalue_after_switch
// DESCRIPTION: Local variable shadows enum constant name (Doom's 'ok' in result_e vs EV_BuildStairs)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok=0
// STDOUT: ok=1
// STDOUT: result=2
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef enum {
    ok,
    crushed,
    pastdest
} result_e;

int main(void) {
    /* 'ok' is an enum constant (value 0) from result_e.
       Doom's EV_BuildStairs declares a local 'int ok;' that shadows it.
       The local variable must be assignable as an lvalue. */
    int ok;
    ok = 0;
    printf("ok=%d\n", ok);
    ok = 1;
    printf("ok=%d\n", ok);
    printf("result=%d\n", (int)pastdest);
    return 0;
}
