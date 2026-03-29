// TEST: logical_and
// DESCRIPTION: Logical AND with short-circuit evaluation
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.13 (Logical AND operator)

int main(void) {
    return 1 && 2;
}
