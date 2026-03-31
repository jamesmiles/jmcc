// TEST: static_global
// DESCRIPTION: static globals should not collide across translation units
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1
// STDOUT: 1
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: 009_helper.c
// NOTE: Requires multi-file compilation support. Will not pass until harness is updated.

int printf(const char *fmt, ...);

static int counter = 0;

int helper_increment(void);

int main(void) {
    counter++;
    printf("%d\n", counter);            /* this file's static counter */
    printf("%d\n", helper_increment()); /* other file's static counter */
    return 0;
}
