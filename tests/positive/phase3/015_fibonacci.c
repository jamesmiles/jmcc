// TEST: fibonacci
// DESCRIPTION: Iterative fibonacci - fib(10) = 55
// EXPECTED_EXIT: 55
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.8.5 (Iteration statements)

int fib(int n) {
    int a = 0;
    int b = 1;
    int i;
    for (i = 0; i < n; i = i + 1) {
        int tmp = b;
        b = a + b;
        a = tmp;
    }
    return a;
}

int main(void) {
    return fib(10);
}
