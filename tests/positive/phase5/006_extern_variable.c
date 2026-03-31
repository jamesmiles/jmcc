// TEST: extern_variable
// DESCRIPTION: extern variable declaration references symbol from another file
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 42
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: 006_helper.c
// NOTE: Requires multi-file compilation support. Will not pass until harness is updated.

int printf(const char *fmt, ...);

extern int shared_var;

int main(void) {
    printf("%d\n", shared_var);
    return 0;
}
