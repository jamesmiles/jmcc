// TEST: bitwise_not
// DESCRIPTION: Bitwise NOT (complement) - ~0 is -1, which as exit code is 255
// EXPECTED_EXIT: 255
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.3.3 (Unary arithmetic operators)

int main(void) {
    return ~0;
}
