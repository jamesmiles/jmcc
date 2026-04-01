// TEST: extern_function
// DESCRIPTION: Cross-file function call (extern linkage)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 84
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: helpers/007_helper.c
// NOTE: Requires multi-file compilation support. Will not pass until harness is updated.

int printf(const char *fmt, ...);

int compute(int x);

int main(void) {
    printf("%d\n", compute(42));
    return 0;
}
