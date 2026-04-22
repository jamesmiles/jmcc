/* Regression: (int)(float_literal * int_constant_expr) must work as a global
 * initialiser on arm64-apple-darwin.
 *
 * Mirrors am_map.c's triangle_guy / thintriangle_guy arrays in Chocolate Doom:
 *
 *   #define R (FRACUNIT)          // FRACUNIT = (1<<16) = 65536 -- integer
 *   mline_t triangle_guy[] = {
 *       { { (fixed_t)(-.867*R), (fixed_t)(-.5*R) }, ... }
 *   };
 *
 * After macro expansion this becomes (fixed_t)(-.867*((1<<16))) where the RHS
 * of the multiply is an integer shift-expression, not a float literal.
 *
 * Test 324 already covers (int)(float * float_literal); this test covers the
 * distinct case of (int)(float_literal * int_constant_expr).
 */
typedef int fixed_t;

typedef struct { fixed_t x, y; } mpoint_t;
typedef struct { mpoint_t a, b; } mline_t;

#define FRACBITS 16
#define FRACUNIT (1<<FRACBITS)

mline_t triangle_guy[] = {
    { { (fixed_t)(-.867*((1<<16))), (fixed_t)(-.5*((1<<16))) },
      { (fixed_t)(.867*((1<<16))),  (fixed_t)(-.5*((1<<16))) } },
    { { (fixed_t)(.867*((1<<16))),  (fixed_t)(-.5*((1<<16))) },
      { (fixed_t)(0),               (fixed_t)(((1<<16)))     } },
    { { (fixed_t)(0),               (fixed_t)(((1<<16)))     },
      { (fixed_t)(-.867*((1<<16))), (fixed_t)(-.5*((1<<16))) } }
};

mline_t thintriangle_guy[] = {
    { { (fixed_t)(-.5*FRACUNIT), (fixed_t)(-.7*FRACUNIT) },
      { (fixed_t)(FRACUNIT),     (fixed_t)(0)            } },
    { { (fixed_t)(FRACUNIT),     (fixed_t)(0)            },
      { (fixed_t)(-.5*FRACUNIT), (fixed_t)(.7*FRACUNIT)  } }
};

int main(void) {
    (void)triangle_guy[0].a.x;
    (void)thintriangle_guy[0].a.x;
    return 0;
}
