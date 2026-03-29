// TEST: prefix_inc
// DESCRIPTION: Prefix increment operator
// EXPECTED_EXIT: 11
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.1 (Prefix increment and decrement operators)

int main(void) {
    int x = 10;
    int y = ++x;
    return y;
}
