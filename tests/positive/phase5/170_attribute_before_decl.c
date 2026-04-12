// TEST: attribute_before_decl
// DESCRIPTION: __attribute__ as first token of a declaration must be accepted
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL headers use __attribute__ before function declarations:
     __attribute__((visibility("default"))) int SDL_Init(int flags);
     __attribute__((always_inline)) static __inline__ int foo(void) { ... }
   jmcc accepts __attribute__ after 'extern' but not as the first
   token of a declaration. This is the most common pattern in SDL
   headers (831+ occurrences of visibility("default")). */

int printf(const char *fmt, ...);

/* __attribute__ as first token of function definition */
__attribute__((visibility("default"))) int visible_func(void) {
    return 42;
}

/* __attribute__ before static inline */
__attribute__((always_inline)) static inline int fast_add(int a, int b) {
    return a + b;
}

/* __attribute__ before variable */
__attribute__((aligned(16))) int aligned_var = 100;

int main(void) {
    if (visible_func() != 42) return 1;
    if (fast_add(3, 4) != 7) return 2;
    if (aligned_var != 100) return 3;

    printf("ok\n");
    return 0;
}
