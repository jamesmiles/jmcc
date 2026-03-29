// TEST: multiple_returns
// DESCRIPTION: Function with multiple return paths
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.8.6.4 (The return statement)

int classify(int x) {
    if (x < 0)
        return 0;
    if (x == 0)
        return 1;
    if (x > 0)
        return 2;
    return 3;
}

int main(void) {
    return classify(42);
}
