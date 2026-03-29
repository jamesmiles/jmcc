// TEST: postfix_inc
// DESCRIPTION: Postfix increment operator (returns old value)
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.2.4 (Postfix increment and decrement operators)

int main(void) {
    int x = 10;
    int y = x++;
    return y;
}
