// TEST: nested_fn_fwd_struct_capture
// DESCRIPTION: GCC nested function capturing a variable of forward-declared struct type
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When `_lift_nested_functions` builds the closure struct for a nested
   function, it must emit the captured variable's type. If that type is
   a struct or typedef that was forward-declared at the point where the
   nested function is parsed (but fully defined by the time code is
   emitted), the lifting pass must defer type resolution rather than
   emitting an incomplete type in the closure struct field.

   Two variants tested:
     1. struct forward-declared above the enclosing function, fully
        defined before it — type is complete by definition time but
        jmcc's lifting pass may snapshot the type too early.
     2. typedef'd struct — same issue, different spelling. */

#include <stdio.h>

/* Forward declaration of struct before outer function */
struct Point;
struct Point { int x; int y; };

int get_x(struct Point p) {
    /* Captures p which has type struct Point (fully defined above) */
    int inner(void) { return p.x; }
    return inner();
}

int get_sum(struct Point p) {
    int sum(void) { return p.x + p.y; }
    return sum();
}

/* typedef variant */
typedef struct { int r; int g; int b; } Color;

int get_green(Color c) {
    int inner(void) { return c.g; }
    return inner();
}

int main(void) {
    struct Point pt = {42, 7};
    if (get_x(pt) != 42) { printf("FAIL get_x: %d\n", get_x(pt)); return 1; }
    if (get_sum(pt) != 49) { printf("FAIL get_sum: %d\n", get_sum(pt)); return 2; }

    Color col = {255, 128, 0};
    if (get_green(col) != 128) { printf("FAIL get_green: %d\n", get_green(col)); return 3; }

    printf("ok\n");
    return 0;
}
