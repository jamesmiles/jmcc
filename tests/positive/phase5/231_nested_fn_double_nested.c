// TEST: nested_fn_double_nested
// DESCRIPTION: GCC nested functions: nested function defined inside another nested function
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* `_lift_nested_functions` currently processes only one level: it lifts
   functions directly nested inside a top-level function body. A nested
   function that itself contains a nested function is not handled —
   after the outer nested function is lifted to file scope, its body
   still contains an inner nested function that was never lifted.

   Two-level deep nesting requires the lifting pass to be applied
   recursively (or iteratively until fixpoint). */

#include <stdio.h>

/* Two levels: inner inside middle inside outer */
int compute(int x) {
    int add_one(int n) {
        int double_it(int m) { return m * 2; }
        return double_it(n) + 1;   /* (n*2)+1 */
    }
    return add_one(x);             /* (x*2)+1 */
}

/* Three levels, no captures */
int three_deep(int x) {
    int f(int n) {
        int g(int m) {
            int h(int k) { return k + 1; }
            return h(m) * 2;       /* (k+1)*2 */
        }
        return g(n) + 3;           /* (n+1)*2 + 3 */
    }
    return f(x);
}

int main(void) {
    /* compute(3) = (3*2)+1 = 7 */
    if (compute(3) != 7) { printf("FAIL compute: got %d\n", compute(3)); return 1; }

    /* three_deep(4) = (4+1)*2 + 3 = 10+3 = 13 */
    if (three_deep(4) != 13) { printf("FAIL three_deep: got %d\n", three_deep(4)); return 2; }

    printf("ok\n");
    return 0;
}
