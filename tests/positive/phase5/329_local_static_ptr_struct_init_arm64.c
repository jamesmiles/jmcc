/* Test: function-local static struct initialised with pointer to another
 * function-local static variable.
 *
 * Reproduces the pattern from Chocolate Doom's hexen/p_map.c:
 *
 *   static vertex_t initvertex1 = {-77594624, 37748736};
 *   static line_t   initslideline = {&initvertex1, NULL, 0, ...};
 *
 * A function-local static (storage class = static, scope = function)
 * requires the same kind of link-time relocation as a file-scope static,
 * but the arm64 code-generator path for struct local-static initialisers
 * does not yet emit the required relocation for an embedded pointer-to-
 * another-local-static value.
 *
 * clang: OK
 * jmcc (arm64-apple-darwin): error: does not yet support this struct
 *   global initializer
 */

#include <stddef.h>

typedef struct { int x; int y; } vertex_t;
typedef struct { vertex_t *v1; vertex_t *v2; int flags; } line_t;

/* Matches the hexen/p_map.c pattern exactly */
void slide_move(void) {
    static vertex_t initvertex1  = {-77594624, 37748736};
    static line_t   initslideline = {&initvertex1, NULL, 0};
    (void)initslideline;
}

int main(void) {
    slide_move();
    return 0;
}
