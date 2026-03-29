// TEST: multiple_vars
// DESCRIPTION: Multiple local variables with arithmetic
// EXPECTED_EXIT: 30
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.7 (Declarations)

int main(void) {
    int a = 10;
    int b = 20;
    return a + b;
}
