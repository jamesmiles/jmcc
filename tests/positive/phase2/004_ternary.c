// TEST: ternary
// DESCRIPTION: Ternary conditional operator
// EXPECTED_EXIT: 5
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.15 (Conditional operator)

int main(void) {
    int x = 10;
    int y = (x > 5) ? 5 : 3;
    return y;
}
