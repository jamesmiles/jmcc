// TEST: parenthesized_expr
// DESCRIPTION: Parenthesized expression overrides precedence
// EXPECTED_EXIT: 20
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.5.1 (Primary expressions)

int main(void) {
    return (2 + 3) * 4;
}
