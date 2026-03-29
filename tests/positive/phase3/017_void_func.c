// TEST: void_func
// DESCRIPTION: Void function that modifies global state
// EXPECTED_EXIT: 100
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.9.1 (Function definitions)

int result = 0;

void compute(int x) {
    result = x * x;
}

int main(void) {
    compute(10);
    return result;
}
