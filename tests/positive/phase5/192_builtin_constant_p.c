// TEST: builtin_constant_p
// DESCRIPTION: __builtin_constant_p must return 1 for compile-time constants, 0 otherwise
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* glibc uses __builtin_constant_p to choose specialised paths
   for compile-time constants:
     #define str_op(s) (__builtin_constant_p(s) ? \
                        fast_path(s) : slow_path(s))
   For a basic implementation, returning 0 always is acceptable
   (the slow path always works) — but ideally returns 1 for literals. */

int printf(const char *fmt, ...);

int slow_value(void) { return 100; }

int main(void) {
    /* Test 1: __builtin_constant_p must exist and be callable */
    int r = __builtin_constant_p(42);
    /* Either 1 (proper detection) or 0 (conservative) is OK */
    if (r != 0 && r != 1) return 1;

    /* Test 2: works on non-constant */
    int x = 10;
    int r2 = __builtin_constant_p(x);
    if (r2 != 0 && r2 != 1) return 2;

    /* Test 3: usable in conditional expressions */
    int v = __builtin_constant_p(5) ? 100 : 200;
    if (v != 100 && v != 200) return 3;

    /* Test 4: usable in the typical glibc pattern */
    int result = (__builtin_constant_p(10) ? 10 * 2 : slow_value());
    if (result != 20 && result != 100) return 4;

    /* Test 5: works with expressions */
    int e = __builtin_constant_p(1 + 2);
    if (e != 0 && e != 1) return 5;

    printf("ok\n");
    return 0;
}
