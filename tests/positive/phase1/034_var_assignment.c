// TEST: var_assignment
// DESCRIPTION: Variable assignment after declaration
// EXPECTED_EXIT: 20
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.16 (Assignment operators)

int main(void) {
    int x = 10;
    x = 20;
    return x;
}
