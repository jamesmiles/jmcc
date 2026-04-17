// TEST: multi_declarator_pointer
// DESCRIPTION: In `T *a, b, c;` only `a` is a pointer; `b` and `c` are plain T
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* The C declarator grammar binds `*` to the individual declarator, not the
   type specifier. So:

       int *p, a, b, c;

   declares p as int*, but a, b, c as plain int.

   jmcc incorrectly propagates the `*` across all declarators, making
   a, b, c all int*. Incrementing `a++` then does pointer arithmetic
   (stride=4) instead of `a+=1`, so `a=5; a++;` yields 9 instead of 6.

   This breaks any code using the C-idiomatic mixed declaration form.
   Rosettacode's topological_sort has:

       struct item_t { const char *name; int *deps, n_deps, idx, depth; };

   where `n_deps, idx, depth` should be plain int but jmcc treats them as
   int*. Every `n_deps++` advances by 4, yielding 4x-too-large counts and
   garbled output. */

#include <stdio.h>

struct S { int *p, a, b, c; };

int main(void) {
    /* Basic: mixed pointer/int in a single declaration */
    int x = 10, y = 20;
    int *a = &x, b = 5;
    if (*a != 10) return 1;
    b++;
    if (b != 6) { printf("FAIL local b: got %d\n", b); return 2; }

    /* Struct field form: same issue, plus struct-access path */
    struct S s = {0};
    s.a = 5;
    s.a++;
    if (s.a != 6) { printf("FAIL s.a: got %d\n", s.a); return 3; }

    s.b = 100;
    s.b += 3;
    if (s.b != 103) { printf("FAIL s.b: got %d\n", s.b); return 4; }

    /* sizeof check — whole struct should be 8 (ptr) + 3*4 (ints) = 20, padded to 24 */
    if (sizeof(struct S) != 24) {
        printf("FAIL sizeof: got %zu want 24\n", sizeof(struct S));
        return 5;
    }

    /* Three pointers then three ints in the SAME declaration */
    int i = 1, j = 2, k = 3;
    int *p1 = &i, *p2 = &j, *p3 = &k, v1 = 100, v2 = 200, v3 = 300;
    v1++; v2++; v3++;
    if (v1 != 101 || v2 != 201 || v3 != 301) {
        printf("FAIL vN: %d %d %d\n", v1, v2, v3);
        return 6;
    }
    if (*p1 + *p2 + *p3 != 6) return 7;

    printf("ok\n");
    return 0;
}
