// TEST: 64bit_basics
// DESCRIPTION: Core 64-bit type sizes, pointer arithmetic, and sizeof must be correct
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Fundamental LP64 assumptions that Doom's 64-bit patches rely on. */

int printf(const char *fmt, ...);

int global_int;
long global_long;
char *global_ptr;

int main(void) {
    /* 1. Type sizes */
    if (sizeof(char) != 1) return 1;
    if (sizeof(short) != 2) return 2;
    if (sizeof(int) != 4) return 3;
    if (sizeof(long) != 8) return 4;
    if (sizeof(void *) != 8) return 5;
    if (sizeof(char *) != 8) return 6;
    if (sizeof(int *) != 8) return 7;
    if (sizeof(long long) != 8) return 8;

    /* 2. sizeof array of pointers */
    void *parr[10];
    int *iarr[5];
    if (sizeof(parr) != 80) return 10;   /* 10 pointers = 80 bytes */
    if (sizeof(iarr) != 40) return 11;

    /* 3. Pointer difference is 64-bit */
    char *a = (char *)0x200000000L;
    char *b = (char *)0x100000000L;
    long diff = a - b;
    if (sizeof(a - b) != 8) return 12;  /* ptrdiff_t should be 8 bytes */

    /* 4. Pointer + int sign extension */
    char *base = (char *)0x100000000L;
    int offset = 16;
    char *result = base + offset;
    if (result != (char *)0x100000010L) return 13;

    /* Negative offset */
    result = base + (-4);
    if (result != (char *)0x0FFFFFFFCL) return 14;

    /* 5. sizeof struct padding */
    struct s1 { int a; void *p; };       /* 4 + 4pad + 8 = 16 */
    struct s2 { void *p; int a; };       /* 8 + 4 + 4pad = 16 */
    struct s3 { int a; int b; void *p; }; /* 4 + 4 + 8 = 16 */
    struct s4 { char c; void *p; };       /* 1 + 7pad + 8 = 16 */
    if (sizeof(struct s1) != 16) return 15;
    if (sizeof(struct s2) != 16) return 16;
    if (sizeof(struct s3) != 16) return 17;
    if (sizeof(struct s4) != 16) return 18;

    /* 6. Pointer in ternary */
    char *x = (char *)0x100000000L;
    char *y = (char *)0x200000000L;
    char *z = (0) ? x : y;
    if (z != y) return 19;

    /* 7. NULL pointer constant */
    char *null = 0;
    if (null != (char *)0) return 20;
    if (null) return 21;

    printf("ok\n");
    return 0;
}
