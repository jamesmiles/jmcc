// TEST: define_expr
// DESCRIPTION: Macro expanding to an expression
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.10.3 (Macro replacement)

#define WIDTH 5
#define HEIGHT 3
#define AREA (WIDTH * HEIGHT)

int main(void) {
    return AREA;
}
