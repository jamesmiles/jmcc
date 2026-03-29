// TEST: negation
// DESCRIPTION: Unary negation (result mod 256 since exit code is byte)
// EXPECTED_EXIT: 246
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.3.3 (Unary arithmetic operators)

int main(void) {
    return -10;
}
