// TEST: func_pointer_call
// DESCRIPTION: Store function address and call indirectly
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 4

int add(int a, int b) { return a + b; }

int apply(void *fp, int a, int b) {
    int (*f)(int, int) = fp;
    return f(a, b);
}

int main(void) {
    return apply(&add, 20, 22);
}
