// TEST: extension_keyword
// DESCRIPTION: __extension__ prefix keyword must be accepted and ignored
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* glibc headers use __extension__ to suppress warnings for GNU
   extensions in -pedantic mode. It appears as a prefix before
   expressions, declarations, and statements. jmcc must accept
   and ignore it. Appears 75 times in SDL preprocessed output. */

int printf(const char *fmt, ...);

int main(void) {
    /* Before expression */
    int x = __extension__ 42;
    if (x != 42) return 1;

    /* Before statement */
    __extension__ typedef unsigned long long u64;
    u64 big = 123456789ULL;
    if (big != 123456789ULL) return 2;

    printf("ok\n");
    return 0;
}
