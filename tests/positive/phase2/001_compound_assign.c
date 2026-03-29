// TEST: compound_assign
// DESCRIPTION: Compound assignment operators (+=, -=, *=, /=, %=)
// EXPECTED_EXIT: 8
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.16.2 (Compound assignment)

int main(void) {
    int x = 10;
    x += 5;
    x -= 3;
    x *= 2;
    x /= 3;
    x %= 9;
    return x;
}
