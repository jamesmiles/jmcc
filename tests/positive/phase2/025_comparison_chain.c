// TEST: comparison_chain
// DESCRIPTION: Chained comparisons using logical operators
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.13, 6.5.14 (Logical operators)

int main(void) {
    int x = 15;
    return (x > 10) && (x < 20) && (x != 12);
}
