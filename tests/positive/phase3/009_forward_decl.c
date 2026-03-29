// TEST: forward_decl
// DESCRIPTION: Forward function declaration
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.6.3 (Function declarators)

int add(int a, int b);

int main(void) {
    return add(3, 7);
}

int add(int a, int b) {
    return a + b;
}
