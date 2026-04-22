/* Regression: float global variables with negative values (unary minus applied
 * to a float literal) and (int)(float_expr) casts in global/static initialisers
 * must work on arm64-apple-darwin.
 *
 * Mirrors am_map.c's triangle_guy / thintriangle_guy arrays which use:
 *   (fixed_t)(-.867 * (1<<16))  and  (fixed_t)(-.5 * (1<<16))
 * as initialiser expressions for mline_t global arrays.
 */

/* Plain negative float globals */
float neg_half  = -0.5f;
float neg_scale = -0.867f;
double neg_pi   = -3.14159;

/* (int)-cast of a float constant expression (fixed-point from float) */
int fixed_neg = (int)(-0.867 * 65536.0);
int fixed_pos = (int)( 0.867 * 65536.0);

/* Nested struct global with (int)(float) initialisers - mirrors am_map.c */
typedef struct { int x, y; } mpoint_t;
typedef struct { mpoint_t a, b; } mline_t;

mline_t triangle_guy[] = {
    { { (int)(-.867*65536.0), (int)(-.5*65536.0) }, { (int)(.867*65536.0), (int)(-.5*65536.0) } },
    { { (int)(.867*65536.0), (int)(-.5*65536.0) }, { (int)(0),             (int)( 65536.0)    } },
    { { (int)(0),            (int)( 65536.0)    }, { (int)(-.867*65536.0), (int)(-.5*65536.0) } }
};

int main(void) {
    (void)(neg_half + neg_scale + neg_pi);
    (void)(fixed_neg + fixed_pos);
    (void)triangle_guy[0].a.x;
    return 0;
}
