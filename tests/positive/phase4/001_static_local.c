// TEST: static_local
// DESCRIPTION: Static local variable persists across function calls
// EXPECTED_EXIT: 3
// ENVIRONMENT: hosted
// PHASE: 4
// STANDARD_REF: 6.2.4 (Storage durations of objects)

int counter(void) {
    static int n = 0;
    n = n + 1;
    return n;
}

int main(void) {
    counter();
    counter();
    return counter();
}
