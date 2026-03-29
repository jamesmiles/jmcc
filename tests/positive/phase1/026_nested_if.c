// TEST: nested_if
// DESCRIPTION: Nested if-else statements
// EXPECTED_EXIT: 3
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.4.1 (The if statement)

int main(void) {
    int x = 15;
    if (x > 20)
        return 1;
    else if (x > 10)
        return 3;
    else
        return 5;
}
