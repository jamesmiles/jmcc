// TEST: macro_arg_recursion
// DESCRIPTION: Blue-paint rule must apply when expanding function-like macro arguments
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* jmcc's preprocessor recursion-crashes on patterns like:
     #define A(x) (x)
     #define B A(B)
     int y = B;
   When expanding B → A(B), the argument B gets recursively expanded
   without propagating the "expanding" set (blue paint). So inner B
   re-expands to A(B) again, indefinitely.

   Fix: when expanding macro arguments at line 832 of preprocessor.py,
   the blue-paint set must be passed through. Each macro name currently
   being expanded must not re-expand inside its own argument.

   This pattern appears in glibc's bits/types.h via __INO_T_TYPE and
   similar typedef chains, blocking compilation of any large codebase
   that includes sys/types.h deeply (SQLite hit this). */

int printf(const char *fmt, ...);

/* Minimal repro: self-referential via function-like macro argument */
#define ID(x) (x)
#define VAL ID(VAL)

/* glibc-style pattern: object macro referencing function macro with same arg */
#define __ULONGWORD_TYPE unsigned long int
#define __STD_TYPE typedef
#define __SYSCALL_ULONG_TYPE __ULONGWORD_TYPE
#define __INO_T_TYPE __SYSCALL_ULONG_TYPE
__STD_TYPE __INO_T_TYPE __ino_t_bypass;

int main(void) {
    /* VAL should expand to ID(VAL) which becomes (VAL) where inner VAL
       is blue-painted. In jmcc this either needs to resolve to (VAL)
       at the C level (VAL as variable name) or handle gracefully. */
    int VAL = 42;
    (void)VAL;

    printf("ok\n");
    return 0;
}
