// TEST: recursive_factorial
// DESCRIPTION: Recursive factorial function
// EXPECTED_EXIT: 120
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.2.2 (Function calls), 6.9.1 (Function definitions)

int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}

int main(void) {
    return factorial(5);
}
