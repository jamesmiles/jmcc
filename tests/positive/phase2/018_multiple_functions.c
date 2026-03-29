// TEST: multiple_functions
// DESCRIPTION: Multiple function definitions and calls
// EXPECTED_EXIT: 25
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.9.1 (Function definitions)

int square(int x) {
    return x * x;
}

int add(int a, int b) {
    return a + b;
}

int main(void) {
    int a = square(3);
    int b = square(4);
    return add(a, b);
}
