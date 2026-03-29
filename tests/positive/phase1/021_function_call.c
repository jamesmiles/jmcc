// TEST: function_call
// DESCRIPTION: Call a user-defined function
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.2.2 (Function calls), 6.9.1 (Function definitions)

int add(int a, int b) {
    return a + b;
}

int main(void) {
    return add(7, 8);
}
