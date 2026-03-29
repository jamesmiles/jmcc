// TEST: if_true
// DESCRIPTION: If statement with true condition
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.4.1 (The if statement)

int main(void) {
    if (1)
        return 1;
    return 0;
}
