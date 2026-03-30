// TEST: conditional_assign
// DESCRIPTION: Conditional assignment with ternary in various contexts
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 3

int abs_val(int x) {
    return x < 0 ? -x : x;
}

int main(void) {
    int a = abs_val(-42);
    int b = abs_val(0);
    return a + b;
}
