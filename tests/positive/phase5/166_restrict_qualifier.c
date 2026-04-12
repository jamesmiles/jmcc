// TEST: restrict_qualifier
// DESCRIPTION: restrict/__restrict/__restrict__ type qualifier must be accepted
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* System headers use __restrict in function prototypes:
     extern int setitimer(int, const void *__restrict, void *__restrict);
   jmcc fails to parse __restrict as a type qualifier.
   This is the second blocker (after __attribute__) preventing
   jmcc from compiling code that includes SDL2 headers. */

int printf(const char *fmt, ...);

/* C99 restrict keyword (and GCC variants) */
void copy(int *restrict dst, const int *restrict src, int n) {
    int i;
    for (i = 0; i < n; i++)
        dst[i] = src[i];
}

/* __restrict variant (used by glibc headers) */
void copy2(int *__restrict dst, const int *__restrict src, int n) {
    int i;
    for (i = 0; i < n; i++)
        dst[i] = src[i];
}

int main(void) {
    int a[] = {1, 2, 3};
    int b[3];

    copy(b, a, 3);
    if (b[0] != 1 || b[2] != 3) return 1;

    copy2(b, a, 3);
    if (b[0] != 1 || b[2] != 3) return 2;

    printf("ok\n");
    return 0;
}
