// TEST: logical_or
// DESCRIPTION: Logical OR with short-circuit evaluation
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.14 (Logical OR operator)

int main(void) {
    return 0 || 1;
}
