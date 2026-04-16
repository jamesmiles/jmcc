// TEST: builtin_offsetof
// DESCRIPTION: __builtin_offsetof must return byte offset of struct member
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* offsetof() from <stddef.h> is usually defined as:
     #define offsetof(TYPE, MEMBER) __builtin_offsetof(TYPE, MEMBER)
   SQLite uses offsetof via stddef.h. jmcc may need to implement
   __builtin_offsetof as a compile-time constant equal to the byte
   offset of the given member within the given struct type. */

int printf(const char *fmt, ...);

typedef struct {
    int a;
    int b;
    char c;
    int d;
    char e[8];
    int f;
} T;

int main(void) {
    /* a at offset 0 */
    if (__builtin_offsetof(T, a) != 0) return 1;
    /* b at offset 4 */
    if (__builtin_offsetof(T, b) != 4) return 2;
    /* c at offset 8 */
    if (__builtin_offsetof(T, c) != 8) return 3;
    /* d at offset 12 (after c + 3-byte padding for int alignment) */
    if (__builtin_offsetof(T, d) != 12) return 4;
    /* e at offset 16 */
    if (__builtin_offsetof(T, e) != 16) return 5;
    /* f at offset 24 */
    if (__builtin_offsetof(T, f) != 24) return 6;

    printf("ok\n");
    return 0;
}
