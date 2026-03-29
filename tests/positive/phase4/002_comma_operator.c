// TEST: comma_operator
// DESCRIPTION: Comma operator evaluates left, returns right
// EXPECTED_EXIT: 3
// ENVIRONMENT: hosted
// PHASE: 4
// STANDARD_REF: 6.5.17 (Comma operator)

int main(void) {
    int x = (1, 2, 3);
    return x;
}
