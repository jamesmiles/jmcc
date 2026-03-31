// TEST: static_function
// DESCRIPTION: static functions should not collide across translation units
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 10
// STDOUT: 20
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: 008_helper.c
// NOTE: Requires multi-file compilation support. Will not pass until harness is updated.

int printf(const char *fmt, ...);

static int helper(void) {
    return 10;
}

int helper_get_value(void);

int main(void) {
    printf("%d\n", helper());           /* this file's static helper */
    printf("%d\n", helper_get_value()); /* other file's static helper */
    return 0;
}
