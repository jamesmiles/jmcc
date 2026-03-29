// TEST: func_macro
// DESCRIPTION: Function-like macro
// EXPECTED_EXIT: 25
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.10.3 (Macro replacement)

#define SQUARE(x) ((x) * (x))

int main(void) {
    return SQUARE(5);
}
