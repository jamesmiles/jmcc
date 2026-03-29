// TEST: if_false
// DESCRIPTION: If statement with false condition
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.4.1 (The if statement)

int main(void) {
    if (0)
        return 1;
    return 0;
}
